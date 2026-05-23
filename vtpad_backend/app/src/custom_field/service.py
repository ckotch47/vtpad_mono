from fastapi import HTTPException

from .model import CustomFieldModel, CustomFieldValueModel
from .dto import *
from ..common.crypto import get_user_id_by_token


class CustomFieldService:
    @staticmethod
    async def create(dto: CustomFieldCreateDto, token: str) -> CustomFieldModel:
        user_id = await get_user_id_by_token(token)
        return await CustomFieldModel.create(
            name=dto.name,
            field_type=dto.field_type,
            entity_type=dto.entity_type,
            options=dto.options or [],
            sort=dto.sort,
            space_id=dto.space_id,
            created_by_id=user_id,
        )

    @staticmethod
    async def get_by_space(space_id: str, entity_type: str = None) -> list[CustomFieldModel]:
        q = CustomFieldModel.filter(space_id=space_id)
        if entity_type:
            q = q.filter(entity_type=entity_type)
        return await q.order_by('sort')

    @staticmethod
    async def get_by_id(field_id: str) -> CustomFieldModel:
        field = await CustomFieldModel.get_or_none(id=field_id)
        if not field:
            raise HTTPException(status_code=404, detail="Custom field not found")
        return field

    @staticmethod
    async def update(field_id: str, dto: CustomFieldUpdateDto) -> CustomFieldModel:
        await CustomFieldService.get_by_id(field_id)
        data = dto.model_dump(exclude_unset=True)
        if data:
            await CustomFieldModel.filter(id=field_id).update(**data)
        return await CustomFieldService.get_by_id(field_id)

    @staticmethod
    async def delete(field_id: str) -> bool:
        await CustomFieldService.get_by_id(field_id)
        await CustomFieldValueModel.filter(field_id=field_id).delete()
        await CustomFieldModel.filter(id=field_id).delete()
        return True


class CustomFieldValueService:
    @staticmethod
    async def set_value(dto: CustomFieldValueDto) -> CustomFieldValueModel:
        await CustomFieldService.get_by_id(dto.field_id)
        existing = await CustomFieldValueModel.get_or_none(field_id=dto.field_id, entity_id=dto.entity_id)
        if existing:
            await CustomFieldValueModel.filter(id=existing.id).update(value=dto.value)
            return await CustomFieldValueModel.get(id=existing.id)
        return await CustomFieldValueModel.create(
            field_id=dto.field_id,
            entity_id=dto.entity_id,
            value=dto.value,
        )

    @staticmethod
    async def get_values(entity_id: str) -> list[CustomFieldValueModel]:
        return await CustomFieldValueModel.filter(entity_id=entity_id).prefetch_related('field')
