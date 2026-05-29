from fastapi import HTTPException
from tortoise import Tortoise

from app.src.admin.roles_enum import RolesEnum
from app.src.common.config import EnvConfig
import logging
logger = logging.getLogger(__name__)

config = EnvConfig()


def get_keys(enum_role):
    temp = []
    for i in enum_role:
        temp.append(i.value)
    return temp


async def check_role_admin(user_payload: dict, available_role: list[RolesEnum]):
    available_role = get_keys(available_role)

    logger.warning(user_payload, available_role)

    if RolesEnum.MAIN_ADMIN in available_role and user_payload.get('id') == config.main_admin_id:
        return True

    conn = Tortoise.get_connection('default')
    sql = "SELECT * FROM usercompanysettingsmodel WHERE user_id = $1"
    this_user = await conn.execute_query_dict(sql, [user_payload.get('id')])
    try:
        if not this_user or not this_user[0]:
            raise HTTPException(status_code=403, detail="not have rule")
        this_user = this_user[0]
        if this_user.get('role') not in available_role:
            raise HTTPException(status_code=403, detail="not have rule")
    except Exception as e:
        logger.error(e, exc_info=True)
        raise HTTPException(status_code=403, detail="not have rule")