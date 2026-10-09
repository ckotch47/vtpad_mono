import hashlib
import html
import json
import logging
import re
from datetime import datetime, time, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType
from tortoise import Tortoise
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from ..common.config import conf
from ..common.crypto import user_payload
from ..common.right_guard import check_user_into_space
from .dto import EmailReportPreviewDto, EmailReportSendDto
from .model import EmailReportDeliveryModel, EmailReportSnapshotModel

logger = logging.getLogger(__name__)

REPORT_MAX_ROWS = 500
REPORT_MAX_PAYLOAD_BYTES = 256 * 1024
SNAPSHOT_TTL = timedelta(hours=24)
REPORT_FIELDS = {'short_name', 'title', 'state', 'created_at', 'updated_at'}
EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?$")


class EmailReportService:
    @staticmethod
    async def _purge_expired_snapshots(limit: int = 100) -> None:
        await Tortoise.get_connection('default').execute_query(
            '''
            DELETE FROM email_report_snapshot
            WHERE id IN (
                SELECT id FROM email_report_snapshot
                WHERE expires_at <= CURRENT_TIMESTAMP
                ORDER BY expires_at
                LIMIT $1
            )
            ''',
            [limit],
        )

    @staticmethod
    async def _authorize_sender(space_id: UUID, request) -> UUID:
        try:
            await check_user_into_space(str(space_id), request)
            authenticated_user_id = getattr(request.state, 'mcp_authenticated_user_id', None)
            if authenticated_user_id is None:
                token = request.headers.get('authorization', '').split(' ', 1)
                if len(token) != 2 or token[0].lower() != 'bearer':
                    raise HTTPException(status_code=401, detail='authentication required')
                authenticated_user_id = user_payload(token[1]).get('id')
            return UUID(str(authenticated_user_id))
        except HTTPException:
            raise
        except (TypeError, ValueError, AttributeError, IndexError) as exc:
            raise HTTPException(status_code=401, detail='authentication required') from exc

    @classmethod
    async def get_recipients(cls, space_id: UUID, request) -> list[dict]:
        await cls._authorize_sender(space_id, request)
        sql = '''
            SELECT DISTINCT u.id, u.username, u.mail
            FROM spacemodel s
            JOIN spacesusermodel su ON su."spaceId" = s.id
            JOIN usermodel u ON u.id = su."userId"
            JOIN usercompanysettingsmodel uc
              ON uc.user_id = u.id
             AND uc.company_id = s.company_id
             AND uc.status = 'active'
            WHERE s.id = $1
              AND u.mail IS NOT NULL
              AND BTRIM(u.mail) <> ''
            ORDER BY u.username, u.mail
        '''
        rows = await Tortoise.get_connection('default').execute_query_dict(sql, [str(space_id)])
        return [{'id': str(row['id']), 'username': row['username'], 'email': row['mail']} for row in rows]

    @classmethod
    async def create_preview(cls, dto: EmailReportPreviewDto, request) -> dict:
        sender_id = await cls._authorize_sender(dto.space_id, request)
        await cls._purge_expired_snapshots()
        start = datetime.combine(dto.date_start, time.min, tzinfo=timezone.utc)
        end_exclusive = datetime.combine(dto.date_end + timedelta(days=1), time.min, tzinfo=timezone.utc)
        conn = Tortoise.get_connection('default')
        create_user_id = str(dto.create_user) if dto.create_user else None
        created_sql = '''
            SELECT short_name, title, state, create_date, update_date
            FROM bugsmodel
            WHERE spaces_id = $1 AND create_date >= $2 AND create_date < $3
              AND ($4::uuid IS NULL OR create_user_id = $4)
            ORDER BY create_date DESC
            LIMIT $5
        '''
        updated_sql = '''
            SELECT short_name, title, state, create_date, update_date
            FROM bugsmodel
            WHERE spaces_id = $1 AND update_date >= $2 AND update_date < $3
              AND ($4::uuid IS NULL OR create_user_id = $4)
              AND DATE_TRUNC('second', update_date) != DATE_TRUNC('second', create_date)
              AND state != 'OPEN'
            ORDER BY update_date DESC
            LIMIT $5
        '''
        created = await conn.execute_query_dict(created_sql, [str(dto.space_id), start, end_exclusive, create_user_id, REPORT_MAX_ROWS + 1])
        updated = await conn.execute_query_dict(updated_sql, [str(dto.space_id), start, end_exclusive, create_user_id, REPORT_MAX_ROWS + 1])
        if len(created) > REPORT_MAX_ROWS or len(updated) > REPORT_MAX_ROWS:
            raise HTTPException(status_code=413, detail='report contains too many rows')

        summary = {
            'opened': len(created),
            'updated': len(updated),
            'open': sum(1 for row in created if row['state'] == 'OPEN'),
            'reopen': sum(1 for row in created if row['state'] == 'REOPEN'),
            'closed': sum(1 for row in created if row['state'] == 'CLOSED'),
            'fixed': sum(1 for row in created if row['state'] == 'FIXED'),
            'hold': sum(1 for row in created if row['state'] == 'HOLD'),
            'ready': sum(1 for row in created if row['state'] == 'READY'),
        }

        def project(row):
            values = {
                'short_name': row.get('short_name'),
                'title': row.get('title'),
                'state': row.get('state'),
                'created_at': row['create_date'].isoformat(),
                'updated_at': row['update_date'].isoformat(),
            }
            return {field: values[field] for field in dto.fields if field in REPORT_FIELDS}

        payload = {
            'fields': list(dto.fields),
            'date_start': dto.date_start.isoformat(),
            'date_end': dto.date_end.isoformat(),
            'created': [project(row) for row in created],
            'updated': [project(row) for row in updated],
        }
        if 'summary' in dto.fields:
            payload['summary'] = summary
        encoded = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        if len(encoded) > REPORT_MAX_PAYLOAD_BYTES:
            raise HTTPException(status_code=413, detail='report payload is too large')

        snapshot = await EmailReportSnapshotModel.create(
            space_id=dto.space_id,
            sender_user_id=sender_id,
            payload=payload,
            expires_at=datetime.now(timezone.utc) + SNAPSHOT_TTL,
        )
        return {'snapshot_id': str(snapshot.id), 'expires_at': snapshot.expires_at.isoformat(), 'payload': payload}

    @classmethod
    async def send(cls, dto: EmailReportSendDto, request) -> dict:
        space_id = await cls._snapshot_space(dto.snapshot_id)
        sender_id = await cls._authorize_sender(space_id, request)
        snapshot = await EmailReportSnapshotModel.filter(
            id=dto.snapshot_id, sender_user_id=sender_id
        ).first()
        if not snapshot:
            raise HTTPException(status_code=404, detail='report snapshot not found')
        if snapshot.expires_at <= datetime.now(timezone.utc):
            await EmailReportSnapshotModel.filter(id=snapshot.id).delete()
            raise HTTPException(status_code=404, detail='report snapshot not found')
        if not conf.use_mail or not getattr(conf, 'mail_conf', None):
            raise HTTPException(status_code=503, detail='email delivery is unavailable')

        recipients = await cls._resolve_recipients(snapshot.space_id, dto.recipient_ids)
        confirmed_emails = {
            str(recipient.recipient_id): recipient.email
            for recipient in dto.confirmed_recipients
        }
        if any(confirmed_emails.get(str(recipient['id'])) != recipient['email'] for recipient in recipients):
            raise HTTPException(status_code=409, detail='recipient details changed; refresh and confirm again')
        request_digest = hashlib.sha256(json.dumps({
            'snapshot_id': str(snapshot.id),
            'recipient_ids': sorted(str(value) for value in dto.recipient_ids),
            'confirmed_recipients': sorted(
                (str(recipient['id']), recipient['email']) for recipient in recipients
            ),
        }, separators=(',', ':')).encode()).hexdigest()

        deliveries = []
        try:
            async with in_transaction() as connection:
                for recipient in recipients:
                    delivery = await EmailReportDeliveryModel.filter(
                        space_id=snapshot.space_id,
                        sender_user_id=sender_id,
                        idempotency_key=dto.idempotency_key,
                        recipient_user_id=recipient['id'],
                    ).using_db(connection).first()
                    if delivery:
                        if delivery.request_digest != request_digest or delivery.snapshot_id != snapshot.id:
                            raise HTTPException(status_code=409, detail='idempotency key was already used')
                        deliveries.append((delivery, recipient, False))
                    else:
                        delivery = await EmailReportDeliveryModel.create(
                            space_id=snapshot.space_id,
                            sender_user_id=sender_id,
                            snapshot_id=snapshot.id,
                            idempotency_key=dto.idempotency_key,
                            recipient_user_id=recipient['id'],
                            request_digest=request_digest,
                            status='pending',
                            using_db=connection,
                        )
                        deliveries.append((delivery, recipient, True))
        except IntegrityError as exc:
            # A concurrent request may have claimed this key. Fail closed; retrying
            # the request will read its durable per-recipient receipts.
            logger.info('Email report delivery claim raced; no additional send performed')
            raise HTTPException(status_code=409, detail='delivery request is already in progress') from exc

        fm = FastMail(conf.mail_conf)
        results = []
        for delivery, recipient, is_new in deliveries:
            if not is_new:
                results.append({'recipient_id': str(recipient['id']), 'status': delivery.status})
                continue
            # Recheck membership immediately before handing the individual message
            # to the mail transport; addresses are always fetched from the DB.
            try:
                current = await cls._resolve_recipients(snapshot.space_id, [recipient['id']])
            except HTTPException as exc:
                if exc.status_code != 422:
                    raise
                await EmailReportDeliveryModel.filter(id=delivery.id).update(status='rejected', error_code='membership_changed')
                results.append({'recipient_id': str(recipient['id']), 'status': 'rejected'})
                continue
            if current[0]['email'] != confirmed_emails[str(recipient['id'])]:
                await EmailReportDeliveryModel.filter(id=delivery.id).update(
                    status='rejected', error_code='recipient_changed'
                )
                results.append({'recipient_id': str(recipient['id']), 'status': 'rejected'})
                continue
            message = MessageSchema(
                subject='VTPad QA report',
                recipients=[current[0]['email']],
                body=cls._render_email(snapshot.payload),
                subtype=MessageType.html,
            )
            try:
                await EmailReportDeliveryModel.filter(id=delivery.id).update(status='sending')
                await fm.send_message(message)
                await EmailReportDeliveryModel.filter(id=delivery.id).update(status='sent', error_code=None)
                results.append({'recipient_id': str(recipient['id']), 'status': 'sent'})
            except Exception:
                # Do not log provider exceptions or addresses. Keep the idempotency
                # receipt so an ambiguous SMTP result cannot cause duplicate mail.
                await EmailReportDeliveryModel.filter(id=delivery.id).update(status='failed', error_code='delivery_failed')
                logger.warning('Email report delivery failed for an individual recipient')
                results.append({'recipient_id': str(recipient['id']), 'status': 'failed'})
        return {'snapshot_id': str(snapshot.id), 'results': results}

    @staticmethod
    async def _snapshot_space(snapshot_id: UUID) -> UUID:
        snapshot = await EmailReportSnapshotModel.filter(id=snapshot_id).only('space_id').first()
        if not snapshot:
            raise HTTPException(status_code=404, detail='report snapshot not found')
        return snapshot.space_id

    @staticmethod
    async def _resolve_recipients(space_id: UUID, recipient_ids: list[UUID]) -> list[dict]:
        sql = '''
            SELECT DISTINCT u.id, u.username, u.mail
            FROM spacemodel s
            JOIN spacesusermodel su ON su."spaceId" = s.id
            JOIN usermodel u ON u.id = su."userId"
            JOIN usercompanysettingsmodel uc
              ON uc.user_id = u.id
             AND uc.company_id = s.company_id
             AND uc.status = 'active'
            WHERE s.id = $1 AND u.id = ANY($2::uuid[])
              AND u.mail IS NOT NULL AND BTRIM(u.mail) <> ''
            ORDER BY u.id
        '''
        rows = await Tortoise.get_connection('default').execute_query_dict(
            sql, [str(space_id), [str(value) for value in recipient_ids]]
        )
        resolved = [{'id': row['id'], 'username': row['username'], 'email': row['mail']} for row in rows]
        if len(resolved) != len(recipient_ids):
            # Identical response for foreign-space, inactive, and nonexistent users.
            raise HTTPException(status_code=422, detail='one or more recipients are unavailable')
        for recipient in resolved:
            email = recipient['email']
            if (
                not isinstance(email, str)
                or len(email) > 254
                or '\r' in email
                or '\n' in email
                or not EMAIL_RE.fullmatch(email)
                or '..' in email
            ):
                raise HTTPException(status_code=422, detail='one or more recipients are unavailable')
        return resolved

    @classmethod
    def _render_email(cls, payload: dict) -> str:
        fields = [field for field in payload.get('fields', []) if field in REPORT_FIELDS]
        labels = {
            'short_name': 'ID', 'title': 'Title', 'state': 'State',
            'created_at': 'Created', 'updated_at': 'Updated',
        }

        def table(title: str, rows: list[dict]) -> str:
            headers = ''.join(f'<th>{html.escape(labels[field])}</th>' for field in fields)
            body = ''.join(
                '<tr>' + ''.join(f'<td>{html.escape(str(row.get(field) or ""))}</td>' for field in fields) + '</tr>'
                for row in rows
            )
            return f'<h2>{title}</h2><table><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table>'

        parts = ['<html><body><h1>QA report</h1>']
        summary = payload.get('summary')
        if isinstance(summary, dict):
            parts.append('<h2>Summary</h2><ul>')
            for key, value in summary.items():
                parts.append(f'<li>{html.escape(key)}: {html.escape(str(value))}</li>')
            parts.append('</ul>')
        parts.append(table('Created', payload.get('created', [])))
        parts.append(table('Updated', payload.get('updated', [])))
        parts.append('</body></html>')
        body = ''.join(parts)
        if len(body.encode('utf-8')) > 1024 * 1024:
            raise HTTPException(status_code=413, detail='email message is too large')
        return body
