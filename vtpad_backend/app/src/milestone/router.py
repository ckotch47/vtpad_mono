from fastapi import APIRouter, Depends

from .service import MilestoneService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/milestone',
    tags=['milestone'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(space_id: str):
    return await MilestoneService.get_by_space(space_id)


@router.get('/{milestone_id}', dependencies=[Depends(bearer)])
async def get_by_id(milestone_id: str):
    return await MilestoneService.get_by_id(milestone_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: MilestoneCreateDto, token: str = Depends(bearer)):
    return await MilestoneService.create(dto, token)


@router.patch('/{milestone_id}', dependencies=[Depends(bearer)])
async def update(milestone_id: str, dto: MilestoneUpdateDto):
    return await MilestoneService.update(milestone_id, dto)


@router.delete('/{milestone_id}', dependencies=[Depends(bearer)])
async def delete(milestone_id: str):
    return await MilestoneService.delete(milestone_id)


@router.post('/{milestone_id}/close', dependencies=[Depends(bearer)])
async def close(milestone_id: str):
    return await MilestoneService.close(milestone_id)
