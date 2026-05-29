from fastapi import APIRouter, Depends

from .service import TestRunService, TestResultService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/test-run',
    tags=['test-run'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(
    space_id: str,
    page: int = 1,
    page_size: int = 25,
    sort_by: Optional[str] = 'created_at',
    sort_order: Optional[str] = 'desc',
    search: Optional[str] = None,
    milestone_id: Optional[str] = None,
    environment_id: Optional[str] = None,
):
    return await TestRunService.get_by_space(space_id, page, page_size, sort_by, sort_order, search, milestone_id, environment_id)


@router.get('/{run_id}', dependencies=[Depends(bearer)])
async def get_by_id(run_id: str):
    run = await TestRunService.get_by_id(run_id)
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
        'created_at': run.created_at.isoformat() if run.created_at else None,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
    }


@router.get('/{run_id}/detail', dependencies=[Depends(bearer)])
async def get_with_results(run_id: str):
    return await TestRunService.get_with_results(run_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TestRunCreateDto, token: str = Depends(bearer)):
    return await TestRunService.create(dto, token)


@router.patch('/{run_id}', dependencies=[Depends(bearer)])
async def update(run_id: str, dto: TestRunUpdateDto):
    return await TestRunService.update(run_id, dto)


@router.post('/{run_id}/start', dependencies=[Depends(bearer)])
async def start(run_id: str):
    return await TestRunService.start(run_id)


@router.post('/{run_id}/complete', dependencies=[Depends(bearer)])
async def complete(run_id: str):
    return await TestRunService.complete(run_id)


@router.delete('/{run_id}', dependencies=[Depends(bearer)])
async def delete(run_id: str):
    return await TestRunService.delete(run_id)


# TestResult endpoints
@router.patch('/result/bulk', dependencies=[Depends(bearer)])
async def bulk_update_results(dto: TestResultBulkUpdateDto, token: str = Depends(bearer)):
    return await TestResultService.bulk_update(dto, token)


@router.patch('/result/{result_id}', dependencies=[Depends(bearer)])
async def update_result(result_id: str, dto: TestResultUpdateDto, token: str = Depends(bearer)):
    return await TestResultService.update_result(result_id, dto, token)



