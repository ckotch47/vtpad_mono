import secrets
import hashlib
from datetime import datetime
from fastapi import HTTPException

from .model import ApiTokenModel
from .dto import *
from ..common.crypto import get_user_id_by_token


class ApiTokenService:
    @staticmethod
    async def create(dto: ApiTokenCreateDto, token: str) -> tuple[str, ApiTokenModel]:
        user_id = await get_user_id_by_token(token)
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        expires = None
        if dto.expires_at:
            expires = datetime.fromisoformat(dto.expires_at.replace('Z', '+00:00'))

        api_token = await ApiTokenModel.create(
            token_hash=token_hash,
            name=dto.name,
            scopes=dto.scopes or [],
            expires_at=expires,
            user_id=user_id,
        )
        return raw_token, api_token

    @staticmethod
    async def get_by_user(token: str) -> list[ApiTokenModel]:
        user_id = await get_user_id_by_token(token)
        return await ApiTokenModel.filter(user_id=user_id).order_by('-created_at')

    @staticmethod
    async def revoke(token_id: str, token: str) -> bool:
        user_id = await get_user_id_by_token(token)
        api_token = await ApiTokenModel.get_or_none(id=token_id, user_id=user_id)
        if not api_token:
            raise HTTPException(status_code=404, detail="Token not found")
        await ApiTokenModel.filter(id=token_id).delete()
        return True

    @staticmethod
    async def validate_token(raw_token: str) -> ApiTokenModel:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        api_token = await ApiTokenModel.get_or_none(token_hash=token_hash)
        if not api_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        if api_token.expires_at and api_token.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        await ApiTokenModel.filter(id=api_token.id).update(last_used_at=datetime.utcnow())
        return api_token
