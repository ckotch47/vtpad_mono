from fastapi import APIRouter, Depends, Request

from .service import MilestoneService
from .dto import *
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix='/v2/milestone',
    tags=['milestone'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(space_id: str, request: Request):
    await check_user_into_space(space_id, request)
    return await MilestoneService.get_by_space(space_id)


@router.get('/{milestone_id}', dependencies=[Depends(bearer)])
async def get_by_id(milestone_id: str, request: Request):
    milestone = await MilestoneService.get_by_id(milestone_id)
    await check_user_into_space(str(milestone.space_id), request)
    return milestone


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: MilestoneCreateDto, request: Request, token: str = Depends(bearer)):
    await check_user_into_space(str(dto.space_id), request, capability="runs")
    return await MilestoneService.create(dto, token)


@router.patch('/{milestone_id}', dependencies=[Depends(bearer)])
async def update(milestone_id: str, dto: MilestoneUpdateDto, request: Request):
    milestone = await MilestoneService.get_by_id(milestone_id)
    await check_user_into_space(str(milestone.space_id), request, capability="runs")
    return await MilestoneService.update(milestone_id, dto)


@router.delete('/{milestone_id}', dependencies=[Depends(bearer)])
async def delete(milestone_id: str, request: Request):
    milestone = await MilestoneService.get_by_id(milestone_id)
    await check_user_into_space(str(milestone.space_id), request, capability="runs")
    return await MilestoneService.delete(milestone_id)


@router.post('/{milestone_id}/close', dependencies=[Depends(bearer)])
async def close(milestone_id: str, request: Request):
    milestone = await MilestoneService.get_by_id(milestone_id)
    await check_user_into_space(str(milestone.space_id), request, capability="runs")
    return await MilestoneService.close(milestone_id)
