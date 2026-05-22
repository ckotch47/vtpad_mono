import json

from tortoise import Tortoise

from .dto import *
from .model import *

from ..common.crypto import *
from ..redis import redis_service


class UserService:
    @staticmethod
    async def create_user(user: RegisterUserDto, client_host: str = "0.0.0.0"):
        this_user = await UserModel.create(
            username=user.username,
            mail=user.mail,
            password=await get_password_hash(user.password),
        )

        temp = {
            'access_token': await create_access_token({"mail": this_user.mail, "id": str(this_user.id)}),
            'refresh_token': await create_refresh_token({"id": str(this_user.id), "host": client_host})
        }

        await redis_service.set_string(f'{this_user.id}_refresh_token', temp['refresh_token'])

        return temp

    @staticmethod
    async def get_user_by_mail(user_mail: str):
        conn = Tortoise.get_connection('default')
        sql = (f"SELECT usermodel.id as id, username, mail, password, \
                   u.status, u.role, \
                   jsonb_build_object('avatar',avatar_id,  'filepath',f.filepath) as avatar, \
                   jsonb_build_object('id', c.id, 'name', c.name, 'status', c.status) as company \
            FROM usermodel \
                LEFT JOIN filemodel f on usermodel.avatar_id = f.id \
                LEFT JOIN usercompanysettingsmodel u on usermodel.id = u.user_id \
                Left JOIN companymodel c on u.company_id = c.id \
            WHERE usermodel.mail = $1  \
                AND u.status = 'active' \
                AND c.status = 'active'")
        try:
            return (await conn.execute_query_dict(sql, [user_mail, ]))[0]
        except Exception as e:
            print(e)
            return None

    @staticmethod
    async def get_user_by_id_with_company_right(user_id: str):
        return []

    @staticmethod
    async def get_user_by_id(user_payload: dict):
        conn = Tortoise.get_connection("default")
        sql = f"SELECT usermodel.id as id, username, mail, avatar_id, f.filepath \
                FROM usermodel \
                    LEFT JOIN filemodel f on usermodel.avatar_id = f.id \
                    LEFT JOIN usercompanysettingsmodel u on usermodel.id = u.user_id \
                    LEFT OUTER JOIN companymodel c on c.id = u.company_id \
                WHERE usermodel.id = $1 \
                AND u.status = 'active' \
                AND c.status = 'active'"
        temp = await conn.execute_query_dict(sql, [user_payload.get('id'), ])
        temp[0]['avatar'] = {"id": temp[0]['avatar_id'], "filepath": temp[0]['filepath']}
        return temp[0]

    @staticmethod
    async def get_user_by_id_V2(user_payload: dict):
        conn = Tortoise.get_connection("default")
        sql = f"SELECT usermodel.id as id, username, mail, \
                   u.status, u.role, \
                   jsonb_build_object('avatar',avatar_id,  'filepath',f.filepath) as avatar, \
                   jsonb_build_object('id', c.id, 'name', c.name, 'status', c.status) as company \
            FROM usermodel \
                LEFT JOIN filemodel f on usermodel.avatar_id = f.id \
                LEFT JOIN usercompanysettingsmodel u on usermodel.id = u.user_id \
                Left JOIN companymodel c on u.company_id = c.id \
            WHERE usermodel.id = $1"
        temp = await conn.execute_query_dict(sql, [user_payload.get("id"), ])
        temp[0]['avatar'] = json.loads(temp[0].get('avatar'))
        temp[0]['company'] = json.loads(temp[0].get('company'))
        return temp[0]

    @staticmethod
    async def update_user(dto: UpdateUserDto, user: dict):
        # self_user = await UserModel.filter(id=user.get('id')).get()
        await UserModel.filter(id=user.get('id')).update(username=dto.username)
        return await UserService.get_user_by_id_V2(user)

    @staticmethod
    async def search_user_by_mail(mail: str, user_payload: dict):
        conn = Tortoise.get_connection('default')
        sql = (f"SELECT usermodel.id, usermodel.username, usermodel.mail, avatar_id FROM usermodel \
                    LEFT OUTER JOIN usercompanysettingsmodel u on usermodel.id = u.user_id \
                WHERE mail LIKE '%{mail}%' \
                AND u.status = 'active' \
                AND u.company_id = "
               f"(SELECT company_id FROM usercompanysettingsmodel WHERE user_id = $1 LIMIT 1)")
        # todo companyID

        return await conn.execute_query_dict(sql, [user_payload.get('id'), ])
