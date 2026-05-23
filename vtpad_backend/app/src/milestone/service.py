from fastapi import HTTPException

from .model import MilestoneModel, MilestoneStatus
from .dto import *
from ..common.crypto import get_user_id_by_token


class MilestoneService:
    @staticmethod
    async def create(dto: MilestoneCreateDto, token: str) -> MilestoneModel:
        user_id = await get_user_id_by_token(token)
        return await MilestoneModel.create(
            title=dto.title,
            description=dto.description,
            start_date=dto.start_date,
            end_date=dto.end_date,
            space_id=dto.space_id,
            created_by_id=user_id,
        )

    @staticmethod
    async def get_by_space(space_id: str) -> list[MilestoneModel]:
        return await MilestoneModel.filter(space_id=space_id).order_by('-created_at')

    @staticmethod
    async def get_by_id(milestone_id: str) -> MilestoneModel:
        ms = await MilestoneModel.get_or_none(id=milestone_id)
        if not ms:
            raise HTTPException(status_code=404, detail="Milestone not found")
        return ms

    @staticmethod
    async def update(milestone_id: str, dto: MilestoneUpdateDto) -> MilestoneModel:
        await MilestoneService.get_by_id(milestone_id)
        data = dto.model_dump(exclude_unset=True)
        if data:
            await MilestoneModel.filter(id=milestone_id).update(**data)
        return await MilestoneService.get_by_id(milestone_id)

    @staticmethod
    async def delete(milestone_id: str) -> bool:
        await MilestoneService.get_by_id(milestone_id)
        await MilestoneModel.filter(id=milestone_id).delete()
        return True

    @staticmethod
    async def close(milestone_id: str) -> MilestoneModel:
        await MilestoneService.get_by_id(milestone_id)
        await MilestoneModel.filter(id=milestone_id).update(status=MilestoneStatus.closed)
        return await MilestoneService.get_by_id(milestone_id)
