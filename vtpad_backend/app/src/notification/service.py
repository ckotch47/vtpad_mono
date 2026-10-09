import json
import logging
from typing import Any

from fastapi import HTTPException
from tortoise import Tortoise
from tortoise.backends.base.client import BaseDBAsyncClient

from .model import NotificationModel
from .dto import CreateNotificationDto, GetNotificationDto
from .enum import EventNotificationEnum

logger = logging.getLogger(__name__)


class NotificationService:
    # A run-scoped notification is visible only while its recipient still has
    # the same active-space access accepted by check_user_into_space.
    _VISIBLE_RUN_NOTIFICATION = """
        (n.run_id IS NULL OR EXISTS (
            SELECT 1
            FROM test_run tr
            JOIN spacemodel s ON s.id = tr.space_id
            WHERE tr.id = n.run_id
              AND (
                EXISTS (
                    SELECT 1
                    FROM spacesusermodel su
                    JOIN usercompanysettingsmodel uc
                      ON uc.user_id = $1
                     AND uc.company_id = s.company_id
                     AND uc.status = 'active'
                    WHERE su."spaceId" = s.id
                      AND su."userId" = $1
                )
                OR EXISTS (
                    SELECT 1
                    FROM usercompanysettingsmodel uc
                    WHERE uc.user_id = $1
                      AND uc.company_id = s.company_id
                      AND uc.status = 'active'
                      AND uc.role = 'company_admin'
                )
              )
        ))
    """

    @staticmethod
    def _visibility_clause() -> str:
        return NotificationService._VISIBLE_RUN_NOTIFICATION

    @staticmethod
    def _validate_page(limit: int, skip: int) -> None:
        if not 1 <= limit <= 100 or not 0 <= skip <= 1_000_000:
            raise HTTPException(status_code=422, detail='Invalid notification page')

    @staticmethod
    def _decode_payload(value: Any) -> Any:
        # asyncpg exposes PostgreSQL JSON columns as strings. Historical bug
        # notifications may themselves contain a JSON-encoded string, so decode
        # at most twice while leaving ordinary text unchanged.
        for _ in range(2):
            if not isinstance(value, str):
                break
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                break
        return value

    @staticmethod
    async def create_run_completed(run: Any, using_db: BaseDBAsyncClient) -> None:
        """Create the allowlisted completion event in the run transition transaction."""
        if not run.created_by_id:
            return

        run_id = str(run.id)
        space_id = str(run.space_id)
        payload = {
            "run_id": run_id,
            "route": f"/space/{space_id}/test-runs/{run_id}",
        }
        await using_db.execute_query(
            """
            INSERT INTO notificationmodel
                (id, create_date, user_id, run_id, data, event, personal, read, send)
            VALUES
                (gen_random_uuid(), CURRENT_TIMESTAMP, $1, $2, $3::json,
                 'RUN_COMPLETED', TRUE, FALSE, FALSE)
            ON CONFLICT (run_id, event, user_id) WHERE run_id IS NOT NULL
            DO NOTHING
            """,
            [run.created_by_id, run_id, json.dumps(payload)],
        )

    @staticmethod
    async def get_notification(dto: GetNotificationDto, limit: int = 20, skip: int = 0):
        NotificationService._validate_page(limit, skip)
        conn = Tortoise.get_connection('default')
        clauses = ['n.user_id = $1', NotificationService._visibility_clause()]
        params: list[Any] = [dto.user_id]
        if dto.send is not None:
            params.append(dto.send)
            clauses.append(f'n.send = ${len(params)}')
        if dto.read is not None:
            params.append(dto.read)
            clauses.append(f'n.read = ${len(params)}')
        if dto.event is not None:
            params.append(dto.event.value)
            clauses.append(f'n.event = ${len(params)}')
        params.extend([skip, limit])
        offset_index, limit_index = len(params) - 1, len(params)
        rows = await conn.execute_query_dict(
            'SELECT n.id, n.create_date, n.user_id, n.data, n.event, n.personal, n.read, n.send '
            'FROM notificationmodel n WHERE ' + ' AND '.join(clauses) +
            f' ORDER BY n.create_date DESC, n.id DESC OFFSET ${offset_index} LIMIT ${limit_index}',
            params,
        )
        for row in rows:
            row['data'] = NotificationService._decode_payload(row['data'])
        return rows

    @staticmethod
    async def add_notification_assign(dto: CreateNotificationDto):
        try:
            existing = await NotificationModel.filter(
                user_id=dto.user,
                data=dto.data,
                event=dto.event,
                personal=dto.personal if dto.personal else True,
                read=dto.read if dto.read else False,
            ).first()
            if existing:
                return None
            return await NotificationModel.create(
                user_id=dto.user,
                data=dto.data,
                event=dto.event,
                personal=dto.personal if dto.personal else True,
                read=dto.read if dto.read else False,
            )
        except Exception:
            logger.exception('Failed to create notification')
            return None

    @staticmethod
    async def update_state_bug(dto: CreateNotificationDto):
        if not dto.user:
            return None
        try:
            return await NotificationModel.create(
                user_id=dto.user,
                data=json.dumps(dto.data),
                event=dto.event,
                personal=dto.personal if dto.personal else True,
                read=dto.read if dto.read else False,
            )
        except Exception:
            logger.exception('Failed to create notification')
            return None

    @staticmethod
    async def read_notification(notification_id: str, user_id: str):
        conn = Tortoise.get_connection('default')
        rows = await conn.execute_query_dict(
            'UPDATE notificationmodel n SET read = TRUE '
            'WHERE n.id = $2 AND n.user_id = $1 AND ' +
            NotificationService._visibility_clause() +
            ' RETURNING n.id, n.create_date, n.user_id, n.data, n.event, n.personal, n.read, n.send',
            [user_id, notification_id],
        )
        if not rows:
            return False
        rows[0]['data'] = NotificationService._decode_payload(rows[0]['data'])
        return rows[0]

    @staticmethod
    async def send_notification(notification_id: str, user_id: str):
        conn = Tortoise.get_connection('default')
        rows = await conn.execute_query_dict(
            'UPDATE notificationmodel n SET send = TRUE '
            'WHERE n.id = $2 AND n.user_id = $1 AND n.send = FALSE AND ' +
            NotificationService._visibility_clause() + ' RETURNING n.id',
            [user_id, notification_id],
        )
        return bool(rows)

    @staticmethod
    async def get_count_unread_notification(user_id: str):
        conn = Tortoise.get_connection('default')
        rows = await conn.execute_query_dict(
            'SELECT COUNT(*) AS count FROM notificationmodel n '
            'WHERE n.user_id = $1 AND n.read = FALSE AND ' +
            NotificationService._visibility_clause(),
            [user_id],
        )
        return int(rows[0]['count']) if rows else 0

    @staticmethod
    async def read_all_notification(user_id: str):
        conn = Tortoise.get_connection('default')
        rows = await conn.execute_query_dict(
            'UPDATE notificationmodel n SET read = TRUE '
            'WHERE n.user_id = $1 AND n.read = FALSE AND ' +
            NotificationService._visibility_clause() + ' RETURNING n.id',
            [user_id],
        )
        return len(rows)
