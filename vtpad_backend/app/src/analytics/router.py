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


@router.get('/space/{space_id}/trend', dependencies=[Depends(bearer)])
async def get_space_trend(space_id: str, days: int = 30):
    return await AnalyticsService.get_space_trend(space_id, days)


@router.get('/space/{space_id}/top-failed', dependencies=[Depends(bearer)])
async def get_top_failed(space_id: str, limit: int = 10):
    return await AnalyticsService.get_top_failed_cases(space_id, limit)


@router.get('/suite/{suite_id}/coverage', dependencies=[Depends(bearer)])
async def get_suite_coverage(suite_id: str):
    return await AnalyticsService.get_suite_coverage(suite_id)
