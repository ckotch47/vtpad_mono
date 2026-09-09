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
    sql = 'SELECT * FROM usermodel \
            LEFT JOIN usercompanysettingsmodel u on usermodel.id = u.user_id \
            LEFT JOIN spacesusermodel sp on sp."userId" = usermodel.id \
            WHERE usermodel.id = $1 \
            AND sp."spaceId" = $2 \
            AND u.status = \'active\''
    sql_user_role = """
        SELECT usercompanysettingsmodel.role FROM usercompanysettingsmodel
        LEFT JOIN spacemodel s on usercompanysettingsmodel.company_id = s.company_id
        WHERE user_id = $1
        AND s.id = $2
    """
    tmp = await conn.execute_query(sql, [user_id, space_id])
    tmp_user_role = await conn.execute_query_dict(sql_user_role, [user_id, space_id])
    if not tmp_user_role:
        raise HTTPException(status_code=403, detail=f'not right space')
    if not bool(tmp[0]) and tmp_user_role[0].get('role') != 'company_admin':
        raise HTTPException(status_code=403, detail=f'not right space')
