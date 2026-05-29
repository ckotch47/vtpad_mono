from fastapi import APIRouter, Depends
from typing import Optional

from .service import AnalyticsService
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/analytics',
    tags=['analytics'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_space_stats(space_id: str):
    return await AnalyticsService.get_space_stats(space_id)


@router.get('/suite/{suite_id}/coverage', dependencies=[Depends(bearer)])
async def get_suite_coverage(suite_id: str):
    return await AnalyticsService.get_suite_coverage(suite_id)
