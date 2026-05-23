from fastapi import HTTPException

from .model import EnvironmentModel
from .dto import *
from ..common.crypto import get_user_id_by_token


class EnvironmentService:
    @staticmethod
    async def create(dto: EnvironmentCreateDto, token: str) -> EnvironmentModel:
        user_id = await get_user_id_by_token(token)
        return await EnvironmentModel.create(
            name=dto.name,
            os=dto.os,
            browser=dto.browser,
            url=dto.url,
            variables=dto.variables,
            space_id=dto.space_id,
            created_by_id=user_id,
        )

    @staticmethod
    async def get_by_space(space_id: str) -> list[EnvironmentModel]:
        return await EnvironmentModel.filter(space_id=space_id).order_by('name')

    @staticmethod
    async def get_by_id(env_id: str) -> EnvironmentModel:
        env = await EnvironmentModel.get_or_none(id=env_id)
        if not env:
            raise HTTPException(status_code=404, detail="Environment not found")
        return env

    @staticmethod
    async def update(env_id: str, dto: EnvironmentUpdateDto) -> EnvironmentModel:
        await EnvironmentService.get_by_id(env_id)
        data = dto.model_dump(exclude_unset=True)
        if data:
            await EnvironmentModel.filter(id=env_id).update(**data)
        return await EnvironmentService.get_by_id(env_id)

    @staticmethod
    async def delete(env_id: str) -> bool:
        await EnvironmentService.get_by_id(env_id)
        await EnvironmentModel.filter(id=env_id).delete()
        return True
