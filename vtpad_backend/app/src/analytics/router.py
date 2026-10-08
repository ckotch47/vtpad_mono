from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from .service import AnalyticsService
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space
from ..test_run.model import TestRunModel
from ..test_suite.model import TestSuiteModel

router = APIRouter(
    prefix='/v2/analytics',
    tags=['analytics'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_space_stats(space_id: str):
    return await AnalyticsService.get_space_stats(space_id)


@router.get('/space/{space_id}/top-failed', dependencies=[Depends(bearer)])
async def get_top_failed(space_id: str, limit: int = 10):
    return await AnalyticsService.get_top_failed(space_id, limit)


@router.get('/space/{space_id}/trend', dependencies=[Depends(bearer)])
async def get_trend(space_id: str, days: int = 30):
    return await AnalyticsService.get_trend(space_id, days)


@router.get('/suite/{suite_id}/coverage', dependencies=[Depends(bearer)])
async def get_suite_coverage(suite_id: str):
    return await AnalyticsService.get_suite_coverage(suite_id)


async def _validate_bug_filters(space_id: UUID, run_id: UUID | None, suite_id: UUID | None) -> None:
    # Missing and foreign IDs have the same response to avoid confirming that a
    # resource exists in another space.
    if run_id is not None and not await TestRunModel.filter(id=run_id, space_id=space_id).exists():
        raise HTTPException(status_code=404, detail='not found')
    if suite_id is not None and not await TestSuiteModel.filter(id=suite_id, space_id=space_id).exists():
        raise HTTPException(status_code=404, detail='not found')


@router.get('/space/{space_id}/bugs', dependencies=[Depends(bearer), Depends(check_user_into_space)])
async def get_linked_bugs(
    space_id: UUID,
    status: Literal['OPEN', 'FIXED', 'REOPEN', 'OTHER'] | None = None,
    run_id: UUID | None = None,
    suite_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    await _validate_bug_filters(space_id, run_id, suite_id)
    return await AnalyticsService.get_linked_bugs(
        str(space_id), page, page_size, status,
        str(run_id) if run_id else None,
        str(suite_id) if suite_id else None,
    )


@router.get('/space/{space_id}/bugs/by-run', dependencies=[Depends(bearer), Depends(check_user_into_space)])
async def get_linked_bugs_by_run(
    space_id: UUID,
    status: Literal['OPEN', 'FIXED', 'REOPEN', 'OTHER'] | None = None,
    run_id: UUID | None = None,
    suite_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    await _validate_bug_filters(space_id, run_id, suite_id)
    return await AnalyticsService.get_linked_bugs_by_run(
        str(space_id), page, page_size, status,
        str(run_id) if run_id else None,
        str(suite_id) if suite_id else None,
    )


@router.get('/space/{space_id}/bugs/by-suite', dependencies=[Depends(bearer), Depends(check_user_into_space)])
async def get_linked_bugs_by_suite(
    space_id: UUID,
    status: Literal['OPEN', 'FIXED', 'REOPEN', 'OTHER'] | None = None,
    run_id: UUID | None = None,
    suite_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    await _validate_bug_filters(space_id, run_id, suite_id)
    return await AnalyticsService.get_linked_bugs_by_suite(
        str(space_id), page, page_size, status,
        str(run_id) if run_id else None,
        str(suite_id) if suite_id else None,
    )
