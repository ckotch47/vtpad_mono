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
    search: Optional[str] = None
):
    return await TestRunService.get_by_space(space_id, page, page_size, sort_by, sort_order, search)


@router.get('/{run_id}', dependencies=[Depends(bearer)])
async def get_by_id(run_id: str):
    return await TestRunService.get_by_id(run_id)


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
@router.patch('/result/{result_id}', dependencies=[Depends(bearer)])
async def update_result(result_id: str, dto: TestResultUpdateDto, token: str = Depends(bearer)):
    return await TestResultService.update_result(result_id, dto, token)


@router.patch('/result/bulk', dependencies=[Depends(bearer)])
async def bulk_update_results(dto: TestResultBulkUpdateDto, token: str = Depends(bearer)):
    return await TestResultService.bulk_update(dto, token)
