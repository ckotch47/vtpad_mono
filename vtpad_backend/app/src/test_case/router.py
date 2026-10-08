from fastapi import APIRouter, Depends, Request
from typing import Optional

from .service import TestCaseService
from .dto import *
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix='/v2/test-case',
    tags=['test-case'],
    responses={404: {"description": "Not found"}},
)


async def _require_testcase_access(testcase_id: str, request: Request):
    testcase = await TestCaseService.get_by_id(testcase_id)
    await check_user_into_space(str(testcase.space_id), request)
    return testcase


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(
    space_id: str,
    request: Request,
    type: Optional[str] = None,
    status: Optional[str] = None,
    suite_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
    sort_by: Optional[str] = 'created_at',
    sort_order: Optional[str] = 'desc',
    search: Optional[str] = None
):
    await check_user_into_space(space_id, request)
    return await TestCaseService.get_by_space(space_id, type, status, suite_id, page, page_size, sort_by, sort_order, search)


@router.get('/suite/{suite_id}', dependencies=[Depends(bearer)])
async def get_by_suite(suite_id: str):
    return await TestCaseService.get_by_suite(suite_id)


@router.get('/section/{section_id}', dependencies=[Depends(bearer)])
async def get_by_section(section_id: str):
    return await TestCaseService.get_by_section(section_id)


@router.get('/{testcase_id}', dependencies=[Depends(bearer)])
async def get_by_id(testcase_id: str, request: Request):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.get_with_versions(testcase_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TestCaseCreateDto, request: Request, token: str = Depends(bearer)):
    await check_user_into_space(dto.space_id, request)
    return await TestCaseService.create(dto, token)


@router.patch('/{testcase_id}', dependencies=[Depends(bearer)])
async def update(testcase_id: str, dto: TestCaseUpdateDto, request: Request, token: str = Depends(bearer)):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.update(testcase_id, dto, token)


@router.post('/{testcase_id}/move', dependencies=[Depends(bearer)])
async def move_testcase(testcase_id: str, dto: TestCaseMoveDto, request: Request):
    await _require_testcase_access(testcase_id, request)
    moved = await TestCaseService.move(testcase_id, dto)
    return {
        'id': str(moved.id),
        'space_id': str(moved.space_id),
        'suite_id': str(moved.suite_id) if moved.suite_id else None,
        'section_id': str(moved.section_id) if moved.section_id else None,
    }


@router.delete('/{testcase_id}', dependencies=[Depends(bearer)])
async def delete(testcase_id: str, request: Request):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.delete(testcase_id)


@router.patch('/sort/{testcase_id}', dependencies=[Depends(bearer)])
async def update_sort(testcase_id: str, dto: TestCaseSortDto, request: Request):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.update_sort(testcase_id, dto)


@router.get('/{testcase_id}/runs', dependencies=[Depends(bearer)])
async def get_case_run_history(
    testcase_id: str,
    request: Request,
    page: int = 1,
    page_size: int = 25,
):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.get_run_history(testcase_id, page, page_size)


@router.get('/{testcase_id}/tech-docs', dependencies=[Depends(bearer)])
async def get_tech_docs(testcase_id: str, request: Request):
    from ..traceability.service import TraceabilityService
    await _require_testcase_access(testcase_id, request)
    return await TraceabilityService.get_docs_for_testcase(testcase_id)


@router.put('/{testcase_id}/tech-docs', dependencies=[Depends(bearer)])
async def replace_tech_docs(testcase_id: str, dto: TestCaseTechDocsReplaceDto, request: Request):
    from ..traceability.service import TraceabilityService
    await _require_testcase_access(testcase_id, request)
    return await TraceabilityService.replace_docs_for_testcase(testcase_id, dto.tech_doc_ids)


@router.get('/{testcase_id}/versions', dependencies=[Depends(bearer)])
async def get_versions(testcase_id: str, request: Request):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.get_versions(testcase_id)


@router.get('/{testcase_id}/versions/diff', dependencies=[Depends(bearer)])
async def diff_versions(testcase_id: str, from_version_id: str, to_version_id: str, request: Request):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.diff_versions(testcase_id, from_version_id, to_version_id)


@router.get('/{testcase_id}/versions/{version_id}', dependencies=[Depends(bearer)])
async def get_version(testcase_id: str, version_id: str, request: Request):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.get_version(testcase_id, version_id)


@router.post('/{testcase_id}/versions/{version_id}/restore', dependencies=[Depends(bearer)])
async def restore_version(testcase_id: str, version_id: str, request: Request, token: str = Depends(bearer)):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.restore_version(testcase_id, version_id, token)


@router.post('/{testcase_id}/duplicate', dependencies=[Depends(bearer)])
async def duplicate_testcase(testcase_id: str, request: Request, token: str = Depends(bearer)):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.duplicate(testcase_id, token)
