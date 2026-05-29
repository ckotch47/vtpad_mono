import json
import secrets

from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr, BaseModel
from starlette.background import BackgroundTasks
from tortoise import Tortoise
from .dto import *
from .model import UserCompanySettingsModel
from ..company.enum import ActiveEnum
from ..roles_enum import RolesEnum
from ...common.crypto import get_password_hash
from ...users.dto import RegisterUserDto
from ...users.model import UserModel
from ...users.service import UserService
from app.src.common.config import conf
import logging
logger = logging.getLogger(__name__)

class EmailSchema(BaseModel):
    email: list[EmailStr]

class UserCompanyService:
    model = UserCompanySettingsModel()

    async def get_user_by_company(self, user_payload: dict):
        conn = Tortoise.get_connection('default')
        company = await self.model.filter(user_id=user_payload.get('id')).get()
        sql = "SELECT usercompanysettingsmodel.id, usercompanysettingsmodel.status, usercompanysettingsmodel.company_id, usercompanysettingsmodel.role, " \
              "json_build_object('id', u.id, 'username', u.username, 'mail', u.mail, " \
              "'avatar_id', u.avatar_id, 'avatar', json_build_object('id', f.id, 'filepath', filepath)) as \"user\" " \
              "FROM usercompanysettingsmodel " \
              "LEFT JOIN usermodel u on u.id = usercompanysettingsmodel.user_id " \
              "LEFT JOIN filemodel f on f.id = u.avatar_id " \
              "WHERE company_id = $1 " \
              "ORDER BY usercompanysettingsmodel.status, u.id "

        temp = await conn.execute_query_dict(sql, [company.__getattribute__('company_id')])
        for i in temp:
            i['user'] = json.loads(i['user'])
        return temp

    async def update_user(self, user_payload: dict, user_id: str, dto: UpdateUserCompanyDto):
        conn = Tortoise.get_connection('default')
        try:
            company = await self.model.filter(user_id=user_payload.get('id')).get()
            sql_get_user = "SELECT usercompanysettingsmodel.id, usercompanysettingsmodel.status, usercompanysettingsmodel.company_id, " \
                           "json_build_object('id', u.id, 'username', u.username, 'mail', u.mail, " \
                           "'avatar_id', u.avatar_id, 'avatar', json_build_object('id', f.id, 'filepath', filepath)) as \"user\" " \
                           "FROM usercompanysettingsmodel " \
                           "LEFT JOIN usermodel u on u.id = usercompanysettingsmodel.user_id " \
                           "LEFT JOIN filemodel f on f.id = u.avatar_id " \
                           "WHERE company_id = $1 " \
                           "AND u.id = $2"
            user = await conn.execute_query_dict(sql_get_user, [company.__getattribute__('company_id'), user_id])

            if not user[0]:
                raise HTTPException(status_code=404, detail="not found user")

            user = json.loads(user[0]['user'])
            await UserModel.filter(id=user['id']).update(username=dto.username, mail=dto.mail)
            await self.model.filter(user_id=user['id'], company_id=company.__getattribute__('company_id')).update(
                status=dto.status)

            return True
        except Exception as e:
            logger.error(e, exc_info=True)
            return False

    async def register_user_company(self, dto: RegisterUserDto, user_payload: dict, background_tasks: BackgroundTasks):
        conn = Tortoise.get_connection('default')
        company = await self.model.filter(user_id=user_payload.get('id')).get()

        company_model = await company.company.get()

        new_user_count = await self.model.filter(company_id=company_model.id).count()

        if new_user_count + 1 > company_model.max_person:
            raise HTTPException(status_code=403, detail="max user")
        user_password = await get_password_hash(dto.password)
        this_user = await UserModel.create(
            username=dto.username,
            mail=dto.mail,
            password=user_password,
        )

        await self.model.create(
            status=ActiveEnum.ACTIVE,
            role=RolesEnum.USER,
            company_id=company.__getattribute__('company_id'),
            user_id=this_user.__getattribute__('id')
        )

        sql_get_user = "SELECT usercompanysettingsmodel.id, usercompanysettingsmodel.status, usercompanysettingsmodel.company_id, " \
                       "json_build_object('id', u.id, 'username', u.username, 'mail', u.mail, " \
                       "'avatar_id', u.avatar_id, 'avatar', json_build_object('id', f.id, 'filepath', filepath)) as \"user\" " \
                       "FROM usercompanysettingsmodel " \
                       "LEFT JOIN usermodel u on u.id = usercompanysettingsmodel.user_id " \
                       "LEFT JOIN filemodel f on f.id = u.avatar_id " \
                       "WHERE company_id = $1 " \
                       "AND u.id = $2"
        user = await conn.execute_query_dict(sql_get_user, [company.__getattribute__('company_id'), this_user.__getattribute__('id')])
        user = user[0]
        user['user'] = json.loads(user['user'])
        background_tasks.add_task(self.send_message_new_user, user['user'], dto.password, background_tasks)
        return user

    async def send_message_new_user(self, user: dict,  password: str, background_task: BackgroundTasks):
        if conf.use_mail:
            fm = FastMail(conf.mail_conf)
            message = MessageSchema(
                subject="Fastapi-Mail module",
                recipients=[user.get('mail')],
                body=f"""
                    <p>You have been added on <a href='{conf.frontend_url}'>{conf.app_name}</a></p>
                    <p>Your credentials: <br> login: {user.get('mail')} <br> password: {password}</p>
                """,
                subtype=MessageType.html)
            background_task.add_task(fm.send_message, message)
        return


    async def reset_password(self, user_id: str, user_payload: dict):
        conn = Tortoise.get_connection('default')
        company = await self.model.filter(user_id=user_payload.get('id')).get()
        sql_get_user = "SELECT usercompanysettingsmodel.id, usercompanysettingsmodel.status, usercompanysettingsmodel.company_id, " \
                       "json_build_object('id', u.id, 'username', u.username, 'mail', u.mail, " \
                       "'avatar_id', u.avatar_id, 'avatar', json_build_object('id', f.id, 'filepath', filepath)) as \"user\" " \
                       "FROM usercompanysettingsmodel " \
                       "LEFT JOIN usermodel u on u.id = usercompanysettingsmodel.user_id " \
                       "LEFT JOIN filemodel f on f.id = u.avatar_id " \
                       "WHERE company_id = $1 " \
                       "AND u.id = $2"

        t_user = await conn.execute_query_dict(sql_get_user, [company.__getattribute__('company_id'), user_id])
        if not t_user or not t_user[0]:
            raise HTTPException(status_code=404, detail="not found")

        t_user = await UserModel.filter(id=user_id).get()
        password = secrets.token_urlsafe(12)
        t_user.password = await get_password_hash(password)
        await t_user.save()
        return {'password': password}

    async def delete_user(self, user_id: str, payload: dict):
        conn = Tortoise.get_connection('default')
        sql = "SELECT * FROM usermodel \
                    LEFT OUTER JOIN usercompanysettingsmodel u on usermodel.id = u.user_id \
                WHERE usermodel.id = $1 \
                AND u.company_id = (SELECT company_id FROM usercompanysettingsmodel WHERE user_id = $2 AND role='company_admin' LIMIT 1) "
        user = (await conn.execute_query_dict(sql, [user_id, payload.get('id')]))[0]
        sql_delete = "DELETE FROM usermodel WHERE id = $1"
        return await conn.execute_query_dict(sql_delete, [user.get('user_id'), ])