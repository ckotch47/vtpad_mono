import json

from fastapi import HTTPException


from ..common.crypto import verify_password, create_access_token, create_refresh_token, decode_refresh, user_payload
from ..users.service import UserService
from ..redis import redis_service
from .dto import *


class AuthService:
    userService = UserService()

    async def authenticate_user(self, user: AuthUserDto, client_host: str | None = None) -> object:
        this_user = await self.userService.get_user_by_mail(user.mail)
        print(this_user)
        if not this_user:
            raise HTTPException(status_code=401, detail="Not user")

        if not await verify_password(user.password, this_user.get('password')):
            raise HTTPException(status_code=401, detail="Wrong password")

        if not json.loads(this_user.get('company'))['id']:
            raise HTTPException(status_code=401, detail="Not user")

        temp = {
            'access_token': await create_access_token({
                "mail": this_user.get('mail'),
                "id": str(this_user.get('id')),
                "role": this_user.get('role'),
                "company": str(json.loads(this_user.get('company'))['id'])
            }),
            'refresh_token': await create_refresh_token({"id": str(this_user.get('id')), "host": client_host})
        }
        await redis_service.set_string(f'{this_user.get("id")}_refresh_token', temp['refresh_token'])
        return temp

    async def refresh_token(self, token: str, host: str) -> object:
        payload = user_payload(token)

        if host != payload.get('host'):
            raise HTTPException(status_code=403, detail="Wrong fingerprint")
        this_user = await self.userService.get_user_by_id({'id': payload.get('id')})
        if not this_user:
            raise HTTPException(status_code=401, detail="Not user")

        redis_cache = await redis_service.get_string(f'{this_user.get("id")}_refresh_token')

        if await decode_refresh(redis_cache) != await decode_refresh(token):
            raise HTTPException(status_code=403, detail="Wrong fingerprint")

        temp = {
            'access_token': await create_access_token({"mail": this_user.get('mail'), "id": str(this_user.get('id'))}),
            'refresh_token': await create_refresh_token({"id": str(this_user.get('id')), "host": payload.get('host')})
        }

        await redis_service.set_string(f'{this_user.get("id")}_refresh_token', temp.get('refresh_token'))

        return temp
