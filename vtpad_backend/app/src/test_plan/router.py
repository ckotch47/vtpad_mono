from fastapi import APIRouter, Depends
from typing import Optional

from .service import TestPlanService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/test-plan',
    tags=['test-plan'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(
    space_id: str,
    page: int = 1,
    page_size: int = 25,
    sort_by: Optional[str] = 'created_at',
    sort_order: Optional[str] = 'desc',
    search: Optional[str] = None
):
    return await TestPlanService.get_by_space(space_id, page, page_size, sort_by, sort_order, search)


@router.get('/{plan_id}', dependencies=[Depends(bearer)])
async def get_by_id(plan_id: str):
    return await TestPlanService.get_by_id(plan_id)


@router.get('/{plan_id}/cases', dependencies=[Depends(bearer)])
async def get_filtered_cases(plan_id: str):
    return await TestPlanService.get_filtered_cases(plan_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TestPlanCreateDto, token: str = Depends(bearer)):
    return await TestPlanService.create(dto, token)


@router.patch('/{plan_id}', dependencies=[Depends(bearer)])
async def update(plan_id: str, dto: TestPlanUpdateDto):
    return await TestPlanService.update(plan_id, dto)


@router.delete('/{plan_id}', dependencies=[Depends(bearer)])
async def delete(plan_id: str):
    return await TestPlanService.delete(plan_id)
