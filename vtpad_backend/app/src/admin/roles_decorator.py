from fastapi import HTTPException
from tortoise import Tortoise

from app.src.admin.roles_enum import RolesEnum
from app.src.common.config import EnvConfig

config = EnvConfig()


def get_keys(enum_role):
    temp = []
    for i in enum_role:
        temp.append(i.value)
    return temp


async def check_role_admin(user_payload: dict, available_role: list[RolesEnum]):
    available_role = get_keys(available_role)

    print(user_payload, available_role)

    if RolesEnum.MAIN_ADMIN in available_role and user_payload.get('id') == config.main_admin_id:
        return True

    conn = Tortoise.get_connection('default')
    sql = f"SELECT * FROM usercompanysettingsmodel WHERE user_id = '{user_payload.get('id')}'"
    this_user = await conn.execute_query_dict(sql)
    try:
        if not this_user or not this_user[0]:
            raise HTTPException(status_code=403, detail="not have rule")
        this_user = this_user[0]
        if this_user.get('role') not in available_role:
            raise HTTPException(status_code=403, detail="not have rule")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=403, detail="not have rule")