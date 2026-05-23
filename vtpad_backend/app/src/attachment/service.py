from fastapi import HTTPException

from .model import AttachmentModel
from .dto import *
from ..common.crypto import get_user_id_by_token


class AttachmentService:
    @staticmethod
    async def create(entity_type: str, entity_id: str, file_id: str, token: str) -> AttachmentModel:
        user_id = await get_user_id_by_token(token)
        return await AttachmentModel.create(
            entity_type=entity_type,
            entity_id=entity_id,
            file_id=file_id,
            uploaded_by_id=user_id,
        )

    @staticmethod
    async def get_by_entity(entity_type: str, entity_id: str) -> list[AttachmentModel]:
        return await AttachmentModel.filter(entity_type=entity_type, entity_id=entity_id).prefetch_related('file')

    @staticmethod
    async def delete(attachment_id: str) -> bool:
        await AttachmentModel.filter(id=attachment_id).delete()
        return True
