import base64
import hashlib
import hmac
import re
import secrets
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from uuid import UUID

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from fastapi import HTTPException
from jose import jwt
from tortoise.transactions import in_transaction

from ..common.config import conf
from ..redis.service import RedisService
from ..test_run.model import TestResultModel, TestRunModel
from .model import PublicRunLinkModel

LINK_TTL = timedelta(days=7)
TOKEN_VERSION = 'v1'
MAX_PUBLIC_CASES = 5000
MAX_PUBLIC_GROUPS = 500
_TOKEN_PATTERN = re.compile(r'^v1_[A-Za-z0-9_-]{43}$')
_RATE_LIMIT_SCRIPT = """
local token_count = redis.call('INCR', KEYS[1])
if token_count == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
local ip_count = redis.call('INCR', KEYS[2])
if ip_count == 1 then redis.call('EXPIRE', KEYS[2], ARGV[1]) end
return {token_count, ip_count}
"""


def _feature_enabled() -> None:
    if not conf.public_run_links_enabled:
        raise HTTPException(status_code=404, detail='Public run links are unavailable')


def _key(version: str = TOKEN_VERSION) -> bytes:
    secret = conf.secret_key
    if not isinstance(secret, str) or len(secret.encode('utf-8')) < 32 or version != TOKEN_VERSION:
        raise HTTPException(status_code=503, detail='Public run links are unavailable')
    try:
        return HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'vtpad:public-run-link:hmac:salt:v1',
            info=b'vtpad:public-run-link:hmac:key:' + version.encode('ascii'),
        ).derive(secret.encode('utf-8'))
    except Exception as exc:
        raise HTTPException(status_code=503, detail='Public run links are unavailable') from exc


def _token_digest(token_bytes: bytes, version: str = TOKEN_VERSION) -> str:
    return hmac.new(_key(version), version.encode('ascii') + b'.' + token_bytes, hashlib.sha256).hexdigest()


def _new_token() -> tuple[str, str]:
    raw = secrets.token_bytes(32)
    encoded = base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')
    return f'{TOKEN_VERSION}_{encoded}', _token_digest(raw)


def _parse_token(token: str) -> tuple[str, str] | None:
    if not _TOKEN_PATTERN.fullmatch(token):
        return None
    encoded = token.split('_', 1)[1]
    try:
        raw = base64.urlsafe_b64decode(encoded + '=')
    except (ValueError, TypeError):
        return None
    if len(raw) != 32 or base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii') != encoded:
        return None
    return _token_digest(raw), TOKEN_VERSION


def _actor_id(request) -> UUID:
    actor_id = getattr(getattr(request, 'state', None), 'mcp_authenticated_user_id', None)
    if actor_id is None:
        authorization = request.headers.get('authorization', '')
        scheme, separator, credential = authorization.partition(' ')
        if not separator or scheme.lower() != 'bearer' or not credential:
            raise HTTPException(status_code=401, detail='Authentication required')
        try:
            payload = jwt.decode(credential, conf.secret_key, algorithms=[conf.algorithm])
            actor_id = payload.get('id')
        except Exception as exc:
            raise HTTPException(status_code=401, detail='Authentication required') from exc
    try:
        return UUID(str(actor_id))
    except (TypeError, ValueError, AttributeError) as exc:
        raise HTTPException(status_code=401, detail='Authentication required') from exc


async def _locked_run_and_authorize(run_id: str, actor_id: UUID, connection):
    try:
        parsed_run_id = UUID(str(run_id))
    except (TypeError, ValueError, AttributeError) as exc:
        raise HTTPException(status_code=404, detail='Test run not found') from exc
    run = await TestRunModel.filter(id=parsed_run_id).using_db(connection).select_for_update().first()
    if run is None:
        raise HTTPException(status_code=404, detail='Test run not found')
    role_rows = await connection.execute_query_dict(
        '''SELECT su.role AS space_role, uc.role AS company_role, uc.status AS company_status
             FROM test_run tr
             JOIN spacemodel s ON s.id = tr.space_id
             JOIN spacesusermodel su ON su."spaceId" = s.id AND su."userId" = $1
             JOIN usercompanysettingsmodel uc ON uc.user_id = $1
                  AND uc.company_id = s.company_id AND uc.status = 'active'
            WHERE tr.id = $2''',
        [str(actor_id), str(parsed_run_id)],
    )
    active_memberships = [row for row in role_rows if row.get('company_status') == 'active']
    if not active_memberships:
        raise HTTPException(status_code=404, detail='Test run not found')
    is_owner = any(row.get('space_role') == 'OWNER' for row in active_memberships)
    is_creator = run.created_by_id is not None and str(run.created_by_id) == str(actor_id)
    is_company_admin = (
        run.created_by_id is not None
        and any(row.get('company_role') == 'company_admin' for row in active_memberships)
    )
    if is_owner or is_creator or is_company_admin:
        return run
    raise HTTPException(status_code=404, detail='Test run not found')


async def create_public_link(run_id: str, request) -> dict:
    _feature_enabled()
    actor_id = _actor_id(request)
    token, digest = _new_token()
    now = datetime.now(timezone.utc)
    expires_at = now + LINK_TTL
    async with in_transaction() as connection:
        run = await _locked_run_and_authorize(run_id, actor_id, connection)
        await PublicRunLinkModel.filter(run_id=run.id, revoked_at__isnull=True).using_db(connection).update(
            revoked_at=now
        )
        link = await PublicRunLinkModel.create(
            run_id=run.id,
            token_digest=digest,
            token_version=TOKEN_VERSION,
            key_version=TOKEN_VERSION,
            created_by_id=actor_id,
            expires_at=expires_at,
            using_db=connection,
        )
    return {'token': token, 'expires_at': link.expires_at.isoformat()}


async def get_public_link_metadata(run_id: str, request) -> dict:
    _feature_enabled()
    actor_id = _actor_id(request)
    async with in_transaction() as connection:
        run = await _locked_run_and_authorize(run_id, actor_id, connection)
        link = await PublicRunLinkModel.filter(run_id=run.id).using_db(connection).order_by('-created_at').first()
    if link is None:
        return {'active': False, 'created_at': None, 'expires_at': None}
    active = link.revoked_at is None and link.expires_at > datetime.now(timezone.utc)
    return {
        'active': active,
        'created_at': link.created_at.isoformat() if link.created_at else None,
        'expires_at': link.expires_at.isoformat() if link.expires_at else None,
    }


async def revoke_public_link(run_id: str, request) -> dict:
    _feature_enabled()
    actor_id = _actor_id(request)
    now = datetime.now(timezone.utc)
    async with in_transaction() as connection:
        run = await _locked_run_and_authorize(run_id, actor_id, connection)
        await PublicRunLinkModel.filter(run_id=run.id, revoked_at__isnull=True).using_db(connection).update(
            revoked_at=now
        )
    return {'revoked': True}


async def _rate_limit(token: str, request) -> None:
    client = getattr(request, 'client', None)
    client_ip = getattr(client, 'host', None)
    if not client_ip:
        raise HTTPException(status_code=503, detail='Public run links are unavailable')
    key = _key()
    token_hash = hashlib.sha256(token[:256].encode('utf-8')).hexdigest()
    ip_hash = hmac.new(key, b'client-ip:' + client_ip.encode('utf-8'), hashlib.sha256).hexdigest()
    redis = RedisService()
    try:
        counts = await redis.redis.eval(
            _RATE_LIMIT_SCRIPT,
            2,
            f'public-run:rate:token:{token_hash}',
            f'public-run:rate:ip:{ip_hash}',
            60,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail='Public run links are unavailable') from exc
    finally:
        try:
            await redis.redis.aclose()
        except Exception:
            pass
    if int(counts[0]) > 30 or int(counts[1]) > 120:
        raise HTTPException(status_code=429, detail='Public run link rate limit exceeded')


def _group_name(snapshot) -> str:
    if not isinstance(snapshot, dict):
        return 'Unassigned'
    path = snapshot.get('section_path')
    if not isinstance(path, list):
        return 'Unassigned'
    names = [
        item.get('name', '').strip()
        for item in path
        if isinstance(item, dict) and isinstance(item.get('name'), str) and item.get('name').strip()
    ]
    name = ' / '.join(names)
    return name[:200] if name else 'Unassigned'


async def _projection(run_id: UUID) -> dict:
    run = await TestRunModel.get_or_none(id=run_id)
    if run is None:
        raise HTTPException(status_code=404, detail='Shared run not found')
    results = await TestResultModel.filter(run_id=run_id).order_by('created_at', 'id').limit(MAX_PUBLIC_CASES + 1)
    if len(results) > MAX_PUBLIC_CASES:
        raise HTTPException(status_code=413, detail='Shared run exceeds the supported size')
    status_names = ('not_run', 'passed', 'failed', 'blocked', 'skipped')
    groups = defaultdict(lambda: {
        'case_count': 0,
        'status_counts': {status: 0 for status in status_names},
        'duration_seconds': 0,
    })
    for result in results:
        group_name = _group_name(result.testcase_snapshot)
        if len(groups) >= MAX_PUBLIC_GROUPS - 1 and group_name not in groups:
            group_name = 'Other groups'
        group = groups[group_name]
        group['case_count'] += 1
        status = result.status.value if hasattr(result.status, 'value') else str(result.status)
        if status in group['status_counts']:
            group['status_counts'][status] += 1
        duration = result.duration_seconds
        if isinstance(duration, int) and not isinstance(duration, bool) and duration >= 0:
            group['duration_seconds'] += duration
    projected_groups = [
        {'name': name, **groups[name]}
        for name in sorted(groups, key=lambda value: (value.casefold(), value))
    ]
    return {
        'run': {'name': run.name, 'status': run.status.value if hasattr(run.status, 'value') else str(run.status)},
        'groups': projected_groups,
    }


async def get_shared_run(token: str, request) -> dict:
    _feature_enabled()
    if not isinstance(token, str):
        token = ''
    await _rate_limit(token, request)
    if len(token) > 128:
        raise HTTPException(status_code=404, detail='Shared run not found')
    parsed = _parse_token(token)
    if parsed is None:
        raise HTTPException(status_code=404, detail='Shared run not found')
    digest, version = parsed
    link = await PublicRunLinkModel.get_or_none(
        token_digest=digest,
        token_version=version,
        key_version=version,
    )
    now = datetime.now(timezone.utc)
    if link is None or link.revoked_at is not None or link.expires_at <= now:
        raise HTTPException(status_code=404, detail='Shared run not found')
    return await _projection(link.run_id)
