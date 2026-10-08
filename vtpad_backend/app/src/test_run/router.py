from fastapi import APIRouter, Depends, Request

from .service import TestRunService, TestResultService
from .dto import *
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix='/v2/test-run',
    tags=['test-run'],
    responses={404: {"description": "Not found"}},
)


async def _require_run_access(run_id: str, request: Request):
    run = await TestRunService.get_by_id(run_id)
    await check_user_into_space(str(run.space_id), request)
    return run


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(
    space_id: str,
    request: Request,
    page: int = 1,
    page_size: int = 25,
    sort_by: Optional[str] = 'created_at',
    sort_order: Optional[str] = 'desc',
    search: Optional[str] = None,
    milestone_id: Optional[str] = None,
    environment_id: Optional[str] = None,
):
    await check_user_into_space(space_id, request)
    return await TestRunService.get_by_space(space_id, page, page_size, sort_by, sort_order, search, milestone_id, environment_id)


@router.get('/{run_id}', dependencies=[Depends(bearer)])
async def get_by_id(run_id: str, request: Request):
    run = await _require_run_access(run_id, request)
    return {
        'id': str(run.id),
        'name': run.name,
        'description': run.description,
        'status': run.status,
        'suite_id': str(run.suite_id) if run.suite_id else None,
        'plan_id': str(run.plan_id) if run.plan_id else None,
        'milestone_id': str(run.milestone_id) if run.milestone_id else None,
        'milestone': {
            'id': str(run.milestone.id),
            'title': run.milestone.title,
            'status': run.milestone.status,
        } if run.milestone else None,
        'environment_id': str(run.environment_id) if run.environment_id else None,
        'environment': {
            'id': str(run.environment.id),
            'name': run.environment.name,
        } if run.environment else None,
        'created_by_id': str(run.created_by_id) if run.created_by_id else None,
        'created_at': run.created_at.isoformat() if run.created_at else None,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        'timer': await TestRunService.get_timer(run_id),
    }


async def _timer_transition_response(run_id: str, run):
    return {
        'id': str(run.id),
        'name': run.name,
        'description': run.description,
        'status': run.status,
        'space_id': str(run.space_id),
        'suite_id': str(run.suite_id) if run.suite_id else None,
        'plan_id': str(run.plan_id) if run.plan_id else None,
        'milestone_id': str(run.milestone_id) if run.milestone_id else None,
        'milestone': {
            'id': str(run.milestone.id),
            'title': run.milestone.title,
            'status': run.milestone.status,
        } if run.milestone else None,
        'environment_id': str(run.environment_id) if run.environment_id else None,
        'environment': {
            'id': str(run.environment.id),
            'name': run.environment.name,
        } if run.environment else None,
        'created_by_id': str(run.created_by_id) if run.created_by_id else None,
        'created_at': run.created_at.isoformat() if run.created_at else None,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        'source_snapshot': run.source_snapshot,
        'timer': await TestRunService.get_timer(run_id),
    }


@router.get('/{run_id}/detail', dependencies=[Depends(bearer)])
async def get_with_results(run_id: str, request: Request):
    await _require_run_access(run_id, request)
    return await TestRunService.get_with_results(run_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TestRunCreateDto, request: Request, token: str = Depends(bearer)):
    await check_user_into_space(dto.space_id, request)
    return await TestRunService.create(dto, token)


@router.post('/preview', dependencies=[Depends(bearer)])
async def preview(dto: TestRunCreateDto, request: Request):
    """Return the server-resolved testcase selection before a run is created."""
    await check_user_into_space(dto.space_id, request)
    return await TestRunService.preview(dto)


@router.patch('/{run_id}', dependencies=[Depends(bearer)])
async def update(run_id: str, dto: TestRunUpdateDto, request: Request):
    await _require_run_access(run_id, request)
    return await TestRunService.update(run_id, dto)


@router.post('/{run_id}/start', dependencies=[Depends(bearer)])
async def start(run_id: str, request: Request, token: str = Depends(bearer)):
    await _require_run_access(run_id, request)
    run = await TestRunService.start(run_id, token)
    return await _timer_transition_response(run_id, run)


@router.post('/{run_id}/pause', dependencies=[Depends(bearer)])
async def pause(run_id: str, request: Request, token: str = Depends(bearer)):
    await _require_run_access(run_id, request)
    run = await TestRunService.pause(run_id, token)
    return await _timer_transition_response(run_id, run)


@router.post('/{run_id}/resume', dependencies=[Depends(bearer)])
async def resume(run_id: str, request: Request, token: str = Depends(bearer)):
    await _require_run_access(run_id, request)
    run = await TestRunService.resume(run_id, token)
    return await _timer_transition_response(run_id, run)


@router.post('/{run_id}/complete', dependencies=[Depends(bearer)])
async def complete(run_id: str, request: Request, token: str = Depends(bearer)):
    await _require_run_access(run_id, request)
    run = await TestRunService.complete(run_id, token)
    return await _timer_transition_response(run_id, run)


@router.delete('/{run_id}', dependencies=[Depends(bearer)])
async def delete(run_id: str, request: Request):
    await _require_run_access(run_id, request)
    return await TestRunService.delete(run_id)


# TestResult endpoints
@router.patch('/result/bulk', dependencies=[Depends(bearer)])
async def bulk_update_results(dto: TestResultBulkUpdateDto, request: Request, token: str = Depends(bearer)):
    return await TestResultService.bulk_update(dto, token, request)


@router.patch('/result/{result_id}', dependencies=[Depends(bearer)])
async def update_result(result_id: str, dto: TestResultUpdateDto, request: Request, token: str = Depends(bearer)):
    return await TestResultService.update_result(result_id, dto, token, request)
