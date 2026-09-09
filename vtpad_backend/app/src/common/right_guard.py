import uuid
from typing import Any

from fastapi import HTTPException
from starlette.requests import Request
from tortoise import Tortoise

from app.src.common.crypto import user_payload


async def check_user_into_space(space_id: uuid.UUID | str = None, request: Request = None):
    conn = Tortoise.get_connection('default')
    # MCPAuthMiddleware records API-token authentication under an MCP-specific
    # key. REST requests retain their existing JWT decoding path.
    user_id = getattr(request.state, 'mcp_authenticated_user_id', None)
    if user_id is None:
        token = request.headers.get('authorization').split(" ")[1]
        user_id = user_payload(token).get('id')
    sql = """
        SELECT su.role AS space_role, u.role AS company_role
        FROM spacemodel s
        LEFT JOIN spacesusermodel su
            ON su."spaceId" = s.id
            AND su."userId" = $1
        LEFT JOIN usercompanysettingsmodel u
            ON u.user_id = $1
            AND u.company_id = s.company_id
            AND u.status = 'active'
        WHERE s.id = $2
    """
    roles = await conn.execute_query_dict(sql, [user_id, space_id])
    for role in roles:
        is_active_member = bool(role.get('space_role')) and bool(role.get('company_role'))
        is_active_company_admin = role.get('company_role') == 'company_admin'
        if is_active_member or is_active_company_admin:
            return

    raise HTTPException(status_code=403, detail='not right space')
