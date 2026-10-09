from fastapi import APIRouter, Depends, Request

from .service import TestSuiteService
from .dto import *
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix='/v2/test-suite',
    tags=['test-suite'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(
    space_id: str,
    request: Request,
    page: int = 1,
    page_size: int = 25,
    sort_by: Optional[str] = 'created_at',
    sort_order: Optional[str] = 'desc',
    search: Optional[str] = None,
    status: Optional[str] = None
):
    await check_user_into_space(space_id, request)
    return await TestSuiteService.get_by_space(space_id, page, page_size, sort_by, sort_order, search, status)


async def _require_suite_capability(suite_id: str, request: Request):
    suite = await TestSuiteService.get_by_id(suite_id)
    await check_user_into_space(str(suite.space_id), request, capability="suites")
    return suite


@router.get('/{suite_id}', dependencies=[Depends(bearer)])
async def get_by_id(suite_id: str):
    return await TestSuiteService.get_by_id(suite_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TestSuiteCreateDto, request: Request, token: str = Depends(bearer)):
    await check_user_into_space(dto.space_id, request, capability="suites")
    return await TestSuiteService.create(dto, token)


@router.patch('/{suite_id}', dependencies=[Depends(bearer)])
async def update(suite_id: str, dto: TestSuiteUpdateDto, request: Request):
    await _require_suite_capability(suite_id, request)
    return await TestSuiteService.update(suite_id, dto)


@router.delete('/{suite_id}', dependencies=[Depends(bearer)])
async def delete(suite_id: str, request: Request):
    await _require_suite_capability(suite_id, request)
    return await TestSuiteService.delete(suite_id)


@router.patch('/sort/{suite_id}', dependencies=[Depends(bearer)])
async def update_sort(suite_id: str, dto: TestSuiteSortDto, request: Request):
    await _require_suite_capability(suite_id, request)
    return await TestSuiteService.update_sort(suite_id, dto)
