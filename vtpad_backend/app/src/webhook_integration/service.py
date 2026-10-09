import base64
import hashlib
import hmac
import json
import os
import secrets
import uuid
from datetime import datetime, timezone

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from fastapi import HTTPException
from pydantic import ValidationError
from tortoise import Tortoise
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from ..common.config import conf
from ..spacesuser.model import SpacesUserModel
from ..test_run.model import TestResultModel, TestResultStatus, TestRunModel
from .dto import WebhookBodyDto, WebhookIntegrationCreateDto
from .model import (
    WebhookAuditEventModel, WebhookIntegrationModel, WebhookNonceModel,
    WebhookRequestModel, WebhookResultMappingModel, WebhookResultProvenanceModel,
    WebhookSecurityFailureBucketModel,
)

MAX_BODY_BYTES = 1024 * 1024
MAX_RESULTS = 1000
RATE_LIMIT = 60
MAX_UNVERIFIED_ATTEMPTS_PER_MINUTE = 120
MAX_NONCE_LENGTH = 128
MAX_TIMESTAMP_LENGTH = 12
NONCE_RETENTION_SECONDS = 600
AUDIT_RETENTION_SECONDS = 30 * 24 * 60 * 60
SECURITY_BUCKET_RETENTION_SECONDS = 24 * 60 * 60
ALLOWED_STATUSES = {item.value for item in TestResultStatus}
_AAD_PREFIX = b'vtpad:webhook-integration:credential:'


def _key_material(version: str | None = None) -> tuple[bytes, str]:
    selected_version = version or conf.webhook_encryption_key_version
    encoded = conf.webhook_encryption_key
    try:
        keyring = json.loads(conf.webhook_encryption_keys) if conf.webhook_encryption_keys else {}
    except (TypeError, ValueError):
        keyring = {}
    if selected_version in keyring:
        encoded = keyring[selected_version]
    elif selected_version != conf.webhook_encryption_key_version:
        encoded = None
    if not encoded or not selected_version:
        raise HTTPException(status_code=503, detail='Webhook credential encryption is not configured')
    try:
        key = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=503, detail='Webhook credential encryption is not configured') from exc
    if len(key) != 32:
        raise HTTPException(status_code=503, detail='Webhook credential encryption is not configured')
    jwt_key = (conf.secret_key or '').encode('utf-8')
    jwt_candidates = [jwt_key]
    try:
        jwt_candidates.append(bytes.fromhex(conf.secret_key))
    except (TypeError, ValueError):
        pass
    try:
        jwt_candidates.append(base64.b64decode(conf.secret_key, validate=True))
    except Exception:
        pass
    if any(hmac.compare_digest(key, candidate) for candidate in jwt_candidates if candidate):
        raise HTTPException(status_code=503, detail='Webhook encryption key must be separate from JWT SECRET_KEY')
    return key, selected_version


def _derive_key(master_key: bytes, integration_id: uuid.UUID, version: str) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(), length=32,
        salt=b'vtpad-webhook-credential-hkdf-v1',
        info=_AAD_PREFIX + version.encode('ascii') + b':' + integration_id.bytes,
    ).derive(master_key)


def _encrypt_secret(secret: bytes, integration_id: uuid.UUID) -> tuple[str, str, str]:
    master_key, version = _key_material()
    nonce = os.urandom(12)
    ciphertext = AESGCM(_derive_key(master_key, integration_id, version)).encrypt(
        nonce, secret, _AAD_PREFIX + integration_id.bytes
    )
    return (
        base64.urlsafe_b64encode(ciphertext).decode('ascii'),
        base64.urlsafe_b64encode(nonce).decode('ascii'),
        version,
    )


def _decrypt_secret(integration: WebhookIntegrationModel) -> bytes:
    master_key, key_version = _key_material(integration.key_version)
    try:
        nonce = base64.urlsafe_b64decode(integration.credential_nonce)
        ciphertext = base64.urlsafe_b64decode(integration.credential_ciphertext)
        return AESGCM(_derive_key(master_key, integration.id, key_version)).decrypt(
            nonce, ciphertext, _AAD_PREFIX + integration.id.bytes
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail='Webhook credential could not be decrypted') from exc


def _credential() -> tuple[str, bytes]:
    secret = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(secret).rstrip(b'=').decode('ascii'), secret


def _safe_metadata(integration: WebhookIntegrationModel, mappings: list[WebhookResultMappingModel]) -> dict:
    return {
        'id': str(integration.id), 'space_id': str(integration.space_id),
        'name': integration.name, 'active': integration.active,
        'run_ids': [str(item) for item in integration.allowed_run_ids],
        'result_mapping_count': len(mappings),
        'credential_hash_prefix': integration.credential_hash_prefix,
        'key_version': integration.key_version,
        'created_at': integration.created_at.isoformat() if integration.created_at else None,
        'updated_at': integration.updated_at.isoformat() if integration.updated_at else None,
        'revoked_at': integration.revoked_at.isoformat() if integration.revoked_at else None,
    }


async def _require_lifecycle_permission(space_id: str, actor_id: str) -> None:
    conn = Tortoise.get_connection('default')
    rows = await conn.execute_query_dict(
        """SELECT su.role AS space_role, u.role AS company_role
             FROM spacemodel s
             LEFT JOIN spacesusermodel su ON su.\"spaceId\" = s.id AND su.\"userId\" = $1
             LEFT JOIN usercompanysettingsmodel u ON u.user_id = $1 AND u.company_id = s.company_id
                  AND u.status = 'active'
            WHERE s.id = $2""",
        [actor_id, space_id],
    )
    if not rows or rows[0]['space_role'] is None:
        raise HTTPException(status_code=404, detail='Webhook integration not found')
    if rows[0]['space_role'] != 'OWNER' and rows[0]['company_role'] != 'company_admin':
        raise HTTPException(status_code=403, detail='Webhook integration access denied')


async def create_integration(dto: WebhookIntegrationCreateDto, request) -> dict:
    from ..common.crypto import user_payload
    actor_id = str(getattr(request.state, 'mcp_authenticated_user_id', None) or user_payload(
        request.headers['authorization'].split(' ', 1)[1]
    ).get('id'))
    await _require_lifecycle_permission(str(dto.space_id), actor_id)
    if len(set(dto.run_ids)) != len(dto.run_ids):
        raise HTTPException(status_code=422, detail='Duplicate run IDs are not allowed')
    allowed_run_count = await TestRunModel.filter(
        id__in=dto.run_ids, space_id=dto.space_id
    ).count()
    if allowed_run_count != len(dto.run_ids):
        raise HTTPException(status_code=422, detail='Allowed runs must belong to the integration space')
    if len({mapping.external_id for mapping in dto.result_mappings}) != len(dto.result_mappings):
        raise HTTPException(status_code=422, detail='External result IDs must be unique')
    if len({str(mapping.result_id) for mapping in dto.result_mappings}) != len(dto.result_mappings):
        raise HTTPException(status_code=422, detail='Each result may be mapped only once')
    result_ids = list(dict.fromkeys(str(mapping.result_id) for mapping in dto.result_mappings))
    results = await TestResultModel.filter(id__in=result_ids).prefetch_related('run')
    by_id = {str(result.id): result for result in results}
    allowed_runs = {str(item) for item in dto.run_ids}
    if len(by_id) != len(result_ids):
        raise HTTPException(status_code=422, detail='Result mapping contains an unknown result')
    for mapping in dto.result_mappings:
        result = by_id[str(mapping.result_id)]
        if str(result.run.space_id) != str(dto.space_id) or str(result.run_id) not in allowed_runs:
            raise HTTPException(status_code=422, detail='Result mapping is outside the allowed runs')
    secret_text, secret_bytes = _credential()
    integration_id = uuid.uuid4()
    cipher, nonce, version = _encrypt_secret(secret_bytes, integration_id)
    async with in_transaction() as connection:
        integration = await WebhookIntegrationModel.create(
            id=integration_id, space_id=dto.space_id, name=dto.name,
            allowed_run_ids=[str(item) for item in dto.run_ids],
            credential_ciphertext=cipher, credential_nonce=nonce,
            key_version=version, credential_hash_prefix=hashlib.sha256(secret_bytes).hexdigest()[:12],
            created_by_id=actor_id, using_db=connection,
        )
        await WebhookResultMappingModel.bulk_create([
            WebhookResultMappingModel(
                integration_id=integration.id, external_id=mapping.external_id,
                result_id=mapping.result_id, run_id=by_id[str(mapping.result_id)].run_id,
            ) for mapping in dto.result_mappings
        ], using_db=connection)
    created_mappings = await WebhookResultMappingModel.filter(integration_id=integration.id)
    return {'integration': _safe_metadata(integration, created_mappings), 'credential': secret_text}


async def _get_integration(integration_id: str) -> WebhookIntegrationModel:
    try:
        integration = await WebhookIntegrationModel.filter(id=integration_id).first()
    except Exception:
        integration = None
    if not integration:
        raise HTTPException(status_code=404, detail='Webhook integration not found')
    return integration


async def read_integration(integration_id: str, request) -> dict:
    integration = await _get_integration(integration_id)
    from ..common.crypto import user_payload
    actor_id = str(getattr(request.state, 'mcp_authenticated_user_id', None) or user_payload(
        request.headers['authorization'].split(' ', 1)[1]
    ).get('id'))
    await _require_lifecycle_permission(str(integration.space_id), actor_id)
    mappings = await WebhookResultMappingModel.filter(integration_id=integration.id)
    return _safe_metadata(integration, mappings)


async def _rotate(integration_id: str, request, revoke: bool) -> dict:
    integration = await _get_integration(integration_id)
    from ..common.crypto import user_payload
    actor_id = str(getattr(request.state, 'mcp_authenticated_user_id', None) or user_payload(
        request.headers['authorization'].split(' ', 1)[1]
    ).get('id'))
    await _require_lifecycle_permission(str(integration.space_id), actor_id)
    async with in_transaction() as connection:
        integration = await WebhookIntegrationModel.filter(id=integration.id).using_db(connection).select_for_update().first()
        if not integration or not integration.active:
            raise HTTPException(status_code=404, detail='Webhook integration not found')
        now = datetime.now(timezone.utc)
        if revoke:
            await WebhookIntegrationModel.filter(id=integration.id).using_db(connection).update(
                active=False, revoked_at=now
            )
            return {'id': str(integration.id), 'active': False, 'revoked_at': now.isoformat()}
        secret_text, secret_bytes = _credential()
        cipher, nonce, version = _encrypt_secret(secret_bytes, integration.id)
        await WebhookIntegrationModel.filter(id=integration.id).using_db(connection).update(
            credential_ciphertext=cipher, credential_nonce=nonce, key_version=version,
            credential_hash_prefix=hashlib.sha256(secret_bytes).hexdigest()[:12],
            updated_at=now,
        )
    return {'id': str(integration.id), 'credential': secret_text, 'key_version': version}


async def rotate_integration(integration_id: str, request) -> dict:
    return await _rotate(integration_id, request, False)


async def revoke_integration(integration_id: str, request) -> dict:
    return await _rotate(integration_id, request, True)


def canonical_message(method: str, path: str, timestamp: str, nonce: str, body: bytes) -> bytes:
    body_hash = hashlib.sha256(body).hexdigest()
    return '\n'.join((method.upper(), path, timestamp, nonce, body_hash)).encode('utf-8')


async def _record_security_failure(
    integration_id: str, request_id: uuid.UUID, error_code: str, connection=None
) -> bool:
    """Aggregate unauthenticated failures; return true once the minute cap is reached."""
    try:
        integration_query = WebhookIntegrationModel.filter(id=integration_id)
        if connection is not None:
            integration_query = integration_query.using_db(connection)
        integration = await integration_query.first()
    except Exception:
        integration = None
    if not integration:
        return False
    now = datetime.now(timezone.utc)
    minute_bucket = now.replace(second=0, microsecond=0)
    retention_cutoff = now.timestamp() - SECURITY_BUCKET_RETENTION_SECONDS
    db = connection or Tortoise.get_connection('default')
    if connection is None:
        async with in_transaction() as tx:
            return await _record_security_failure(integration_id, request_id, error_code, connection=tx)
    locked = await WebhookIntegrationModel.filter(id=integration.id).using_db(connection).select_for_update().first()
    if not locked:
        return False
    count_rows = await db.execute_query_dict(
        """SELECT COALESCE(SUM(attempt_count), 0) AS attempts
             FROM webhook_security_failure_bucket
            WHERE integration_id = $1 AND minute_bucket = $2""",
        [integration.id, minute_bucket],
    )
    attempts = int(count_rows[0]['attempts']) if count_rows else 0
    capped = attempts >= MAX_UNVERIFIED_ATTEMPTS_PER_MINUTE
    if not capped:
        await db.execute_query(
            """INSERT INTO webhook_security_failure_bucket
                     (id, integration_id, minute_bucket, last_request_id, error_code, attempt_count, updated_at)
                 VALUES (gen_random_uuid(), $1, $2, $3, $4, 1, $5)
                 ON CONFLICT (integration_id, minute_bucket, error_code)
                 DO UPDATE SET last_request_id = EXCLUDED.last_request_id,
                               attempt_count = webhook_security_failure_bucket.attempt_count + 1,
                               updated_at = EXCLUDED.updated_at""",
            [integration.id, minute_bucket, request_id, error_code, now],
        )
    cleanup = WebhookSecurityFailureBucketModel.filter(
        integration_id=integration.id, minute_bucket__lt=datetime.fromtimestamp(retention_cutoff, timezone.utc)
    )
    if connection is not None:
        cleanup = cleanup.using_db(connection)
    await cleanup.delete()
    return capped


async def record_transport_failure(integration_id: str, error_code: str) -> bool:
    """Record a transport-level rejection without persisting request data."""
    return await _record_security_failure(integration_id, uuid.uuid4(), error_code)


async def _update_audit_event(
    request_id: uuid.UUID, status: str, error_code: str | None = None, result_count: int | None = None
) -> None:
    updates = {'status': status, 'error_code': error_code}
    if result_count is not None:
        updates['result_count'] = result_count
    await WebhookAuditEventModel.filter(request_id=request_id).update(**updates)


async def _reserve_verified_attempt(
    integration: WebhookIntegrationModel, observed_ciphertext: str,
    observed_key_version: str, nonce_hash: str, request_id: uuid.UUID,
) -> str | None:
    """Serialize verified attempts, enforce per-integration quota and reserve the nonce."""
    result: str | None = None
    now = datetime.now(timezone.utc)
    async with in_transaction() as connection:
        locked = await WebhookIntegrationModel.filter(id=integration.id).using_db(connection).select_for_update().first()
        if not locked or not locked.active:
            result = 'integration_inactive'
            await WebhookAuditEventModel.create(
                integration_id=integration.id, request_id=request_id, status='rejected',
                error_code=result, using_db=connection,
            )
        elif (
            locked.key_version != observed_key_version
            or not hmac.compare_digest(locked.credential_ciphertext, observed_ciphertext)
        ):
            result = 'credential_rotated'
            await WebhookAuditEventModel.create(
                integration_id=integration.id, request_id=request_id, status='rejected',
                error_code=result, using_db=connection,
            )
        else:
            await WebhookNonceModel.filter(
                integration_id=integration.id,
                created_at__lt=datetime.fromtimestamp(now.timestamp() - NONCE_RETENTION_SECONDS, timezone.utc),
            ).using_db(connection).delete()
            nonce_seen = await WebhookNonceModel.filter(
                integration_id=integration.id, nonce_hash=nonce_hash
            ).using_db(connection).exists()
            count = await WebhookAuditEventModel.filter(
                integration_id=integration.id,
                created_at__gte=datetime.fromtimestamp(now.timestamp() - 60, timezone.utc),
            ).using_db(connection).count()
            if nonce_seen:
                result = 'nonce_replay'
            elif count >= RATE_LIMIT:
                result = 'rate_limited'
            if result == 'rate_limited':
                await _record_security_failure(
                    str(integration.id), request_id, result, connection=connection
                )
            elif result == 'nonce_replay':
                await WebhookAuditEventModel.create(
                    integration_id=integration.id, request_id=request_id, status='rejected',
                    error_code=result, using_db=connection,
                )
            if not result:
                await WebhookNonceModel.create(
                    integration_id=integration.id, nonce_hash=nonce_hash, using_db=connection
                )
                await WebhookAuditEventModel.create(
                    integration_id=integration.id, request_id=request_id,
                    status='received', using_db=connection,
                )
                await WebhookAuditEventModel.filter(
                    integration_id=integration.id,
                    created_at__lt=datetime.fromtimestamp(now.timestamp() - AUDIT_RETENTION_SECONDS, timezone.utc),
                ).using_db(connection).delete()
    return result


async def process_webhook(
    integration_id: str, method: str, path: str, timestamp: str, nonce: str,
    idempotency_key: str, signature: str, body: bytes,
) -> dict:
    request_id = uuid.uuid4()
    expected_path = f'/api/v2/webhooks/integrations/{integration_id}/callback'
    if method.upper() != 'POST' or path != expected_path:
        await _record_security_failure(integration_id, request_id, 'invalid_request_target')
        raise HTTPException(status_code=400, detail='Invalid webhook request target')
    if len(body) > MAX_BODY_BYTES:
        await _record_security_failure(integration_id, request_id, 'payload_too_large')
        raise HTTPException(status_code=413, detail='Webhook payload exceeds 1 MiB')
    if (
        len(idempotency_key) > 128 or not idempotency_key.strip()
        or len(nonce) < 16 or len(nonce) > MAX_NONCE_LENGTH
        or not nonce.isascii() or any(ord(char) < 0x20 or ord(char) > 0x7e for char in nonce)
    ):
        capped = await _record_security_failure(integration_id, request_id, 'invalid_request_metadata')
        raise HTTPException(status_code=429 if capped else 400, detail='Invalid webhook request metadata')
    integration = await _get_integration(integration_id)
    if not integration.active:
        await _record_security_failure(integration_id, request_id, 'integration_inactive')
        raise HTTPException(status_code=404, detail='Webhook integration not found')
    if len(timestamp) > MAX_TIMESTAMP_LENGTH or not timestamp.isascii() or not timestamp.isdigit():
        capped = await _record_security_failure(integration_id, request_id, 'invalid_timestamp')
        raise HTTPException(status_code=429 if capped else 401, detail='Invalid webhook signature')
    try:
        timestamp_value = int(timestamp)
    except (TypeError, ValueError) as exc:
        capped = await _record_security_failure(integration_id, request_id, 'invalid_timestamp')
        if capped:
            raise HTTPException(status_code=429, detail='Webhook authentication rate limit exceeded') from exc
        raise HTTPException(status_code=401, detail='Invalid webhook signature') from exc
    now_epoch = int(datetime.now(timezone.utc).timestamp())
    if abs(now_epoch - timestamp_value) > 300:
        capped = await _record_security_failure(integration_id, request_id, 'timestamp_window')
        raise HTTPException(status_code=429 if capped else 401, detail='Webhook timestamp outside allowed window')
    if (
        len(signature) != 64 or not signature.isascii()
        or any(char not in '0123456789abcdefABCDEF' for char in signature)
    ):
        capped = await _record_security_failure(integration_id, request_id, 'invalid_signature')
        raise HTTPException(status_code=429 if capped else 401, detail='Invalid webhook signature')
    secret = _decrypt_secret(integration)
    expected = hmac.new(secret, canonical_message(method, path, timestamp, nonce, body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature.lower()):
        capped = await _record_security_failure(integration_id, request_id, 'invalid_signature')
        raise HTTPException(status_code=429 if capped else 401, detail='Invalid webhook signature')
    nonce_hash = hashlib.sha256(nonce.encode()).hexdigest()
    reservation_error = await _reserve_verified_attempt(
        integration, integration.credential_ciphertext, integration.key_version, nonce_hash, request_id
    )
    if reservation_error:
        status_code = 429 if reservation_error == 'rate_limited' else 409 if reservation_error == 'nonce_replay' else 401
        detail = 'Webhook rate limit exceeded' if status_code == 429 else 'Invalid webhook credential state'
        raise HTTPException(status_code=status_code, detail=detail)
    try:
        try:
            raw_payload = json.loads(body)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail='Invalid webhook payload') from exc
        if isinstance(raw_payload, dict) and isinstance(raw_payload.get('results'), list) and len(raw_payload['results']) > MAX_RESULTS:
            raise HTTPException(status_code=413, detail='Webhook event exceeds 1000 results')
        try:
            payload = WebhookBodyDto.model_validate(raw_payload)
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail='Invalid webhook payload') from exc
        if len(payload.results) > MAX_RESULTS:
            raise HTTPException(status_code=413, detail='Webhook event exceeds 1000 results')
        if any(item.status not in ALLOWED_STATUSES for item in payload.results):
            raise HTTPException(status_code=422, detail='Webhook result contains an unsupported status')
        mappings = await WebhookResultMappingModel.filter(integration_id=integration.id)
        mapping_by_external = {item.external_id: item for item in mappings}
        if len({item.external_id for item in payload.results}) != len(payload.results):
            raise HTTPException(status_code=422, detail='Duplicate external result IDs are not allowed')
        unknown = [item.external_id for item in payload.results if item.external_id not in mapping_by_external]
        if unknown:
            raise HTTPException(status_code=422, detail='Webhook contains an unmapped external result ID')
        mapped = [mapping_by_external[item.external_id] for item in payload.results]
        allowlist = {str(item) for item in integration.allowed_run_ids}
        if any(str(item.run_id) not in allowlist for item in mapped):
            raise HTTPException(status_code=403, detail='Webhook result is outside the allowed run scope')
        payload_hash = hashlib.sha256(str(integration.space_id).encode() + b'\0' + body).hexdigest()
        async with in_transaction() as connection:
            locked = await WebhookIntegrationModel.filter(id=integration.id).using_db(connection).select_for_update().first()
            if not locked or not locked.active:
                raise HTTPException(status_code=404, detail='Webhook integration not found')
            if (
                locked.key_version != integration.key_version
                or not hmac.compare_digest(locked.credential_ciphertext, integration.credential_ciphertext)
            ):
                raise HTTPException(status_code=401, detail='Webhook credential was rotated')
            prior = await WebhookRequestModel.filter(
                integration_id=integration.id,
                idempotency_key=hashlib.sha256(idempotency_key.encode('utf-8')).hexdigest(),
            ).using_db(connection).first()
            if prior:
                if prior.payload_hash != payload_hash:
                    raise HTTPException(status_code=409, detail='Idempotency key is already bound to another payload')
                # A replay under a fresh signature nonce returns the durable receipt without reapplying writes.
                replay = {
                    'request_id': str(prior.request_id), 'status': prior.status,
                    'result_count': prior.result_count, 'replayed': True,
                }
            else:
                replay = None
            if replay is None:
                await WebhookRequestModel.create(
                    integration_id=integration.id, request_id=request_id,
                    idempotency_key=hashlib.sha256(idempotency_key.encode('utf-8')).hexdigest(),
                    payload_hash=payload_hash, nonce_hash=nonce_hash,
                    status='accepted', result_count=len(payload.results), using_db=connection,
                )
                result_ids = [item.result_id for item in mapped]
                locked_runs = await TestRunModel.filter(
                    id__in=[item.run_id for item in mapped], space_id=integration.space_id
                ).using_db(connection).order_by('id').select_for_update()
                active_run_ids = {str(item.id) for item in locked_runs if item.status == 'active'}
                results = await TestResultModel.filter(
                    id__in=result_ids
                ).using_db(connection).order_by('id').select_for_update()
                result_by_id = {str(item.id): item for item in results}
                if len(result_by_id) != len(result_ids):
                    raise HTTPException(status_code=422, detail='Mapped result is no longer available')
                now = datetime.now(timezone.utc)
                for item in payload.results:
                    mapping = mapping_by_external[item.external_id]
                    result = result_by_id[str(mapping.result_id)]
                    if (
                        str(result.run_id) not in allowlist
                        or str(result.run_id) not in active_run_ids
                        or str(mapping.run_id) != str(result.run_id)
                    ):
                        raise HTTPException(status_code=403, detail='Mapped result is outside the allowed scope')
                    update_data = {'status': item.status}
                    if 'duration_seconds' in item.model_fields_set:
                        update_data['duration_seconds'] = item.duration_seconds
                    if 'comment' in item.model_fields_set:
                        update_data['comment'] = item.comment
                    update_data['updated_at'] = now
                    await TestResultModel.filter(id=result.id).using_db(connection).update(**update_data)
                    provenance_values = {
                        'integration_id': integration.id, 'integration_name': integration.name,
                        'request_id': request_id, 'updated_at': now,
                    }
                    updated_provenance = await WebhookResultProvenanceModel.filter(
                        result_id=result.id
                    ).using_db(connection).update(**provenance_values)
                    if not updated_provenance:
                        await WebhookResultProvenanceModel.create(
                            result_id=result.id, **provenance_values, using_db=connection
                        )
        if replay:
            await _update_audit_event(request_id, 'replayed', result_count=replay['result_count'])
            return replay
        await _update_audit_event(request_id, 'accepted', result_count=len(payload.results))
        return {'request_id': str(request_id), 'status': 'accepted', 'result_count': len(payload.results), 'replayed': False}
    except HTTPException as exc:
        await _update_audit_event(request_id, 'rejected', f'http_{exc.status_code}')
        raise
    except IntegrityError as exc:
        await _update_audit_event(request_id, 'rejected', 'transaction_conflict')
        raise HTTPException(status_code=409, detail='Webhook request was already processed') from exc
    except Exception:
        await _update_audit_event(request_id, 'rejected', 'processing_error')
        raise
