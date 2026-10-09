from fastapi import APIRouter, Depends, Query, Request
from typing import Optional

from .service import TestCaseService
from .dto import *
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space
from ..test_suite.model import TestSuiteModel
from ..section.model import SectionModel

router = APIRouter(
    prefix='/v2/test-case',
    tags=['test-case'],
    responses={404: {"description": "Not found"}},
)


async def _require_testcase_access(testcase_id: str, request: Request, capability: str | None = None):
    testcase = await TestCaseService.get_by_id(testcase_id)
    await check_user_into_space(str(testcase.space_id), request, capability=capability)
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
    search: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = Query(default=None),
):
    await check_user_into_space(space_id, request)
    return await TestCaseService.get_by_space(
        space_id, type, status, suite_id, page, page_size, sort_by, sort_order,
        search, priority, tags,
    )


@router.get('/space/{space_id}/tags', dependencies=[Depends(bearer)])
async def get_tag_options(space_id: str, request: Request):
    await check_user_into_space(space_id, request)
    return await TestCaseService.get_tag_options(space_id)


@router.get('/suite/{suite_id}', dependencies=[Depends(bearer)])
async def get_by_suite(suite_id: str, request: Request):
    suite = await TestSuiteModel.get_or_none(id=suite_id)
    if not suite:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Test suite not found")
    await check_user_into_space(str(suite.space_id), request)
    cases = await TestCaseService.get_by_suite(suite_id)
    return await TestCaseService.serialize_cases(cases)


@router.get('/section/{section_id}', dependencies=[Depends(bearer)])
async def get_by_section(section_id: str, request: Request):
    section = await SectionModel.get_or_none(id=section_id)
    if not section:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Section not found")
    suite = await TestSuiteModel.get_or_none(id=section.suite_id)
    if not suite:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Section not found")
    await check_user_into_space(str(suite.space_id), request)
    cases = await TestCaseService.get_by_section(section_id)
    return await TestCaseService.serialize_cases(cases)


@router.get('/{testcase_id}', dependencies=[Depends(bearer)])
async def get_by_id(testcase_id: str, request: Request):
    await _require_testcase_access(testcase_id, request)
    return await TestCaseService.get_with_versions(testcase_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TestCaseCreateDto, request: Request, token: str = Depends(bearer)):
    await check_user_into_space(dto.space_id, request, capability="cases")
    case = await TestCaseService.create(dto, token)
    return await TestCaseService.serialize_case(case)


@router.patch('/{testcase_id}', dependencies=[Depends(bearer)])
async def update(testcase_id: str, dto: TestCaseUpdateDto, request: Request, token: str = Depends(bearer)):
    await _require_testcase_access(testcase_id, request, capability="cases")
    case = await TestCaseService.update(testcase_id, dto, token)
    return await TestCaseService.serialize_case(case)


@router.post('/{testcase_id}/move', dependencies=[Depends(bearer)])
async def move_testcase(testcase_id: str, dto: TestCaseMoveDto, request: Request):
    await _require_testcase_access(testcase_id, request, capability="cases")
    moved = await TestCaseService.move(testcase_id, dto)
    return {
        'id': str(moved.id),
        'space_id': str(moved.space_id),
        'suite_id': str(moved.suite_id) if moved.suite_id else None,
        'section_id': str(moved.section_id) if moved.section_id else None,
    }


@router.delete('/{testcase_id}', dependencies=[Depends(bearer)])
async def delete(testcase_id: str, request: Request):
    await _require_testcase_access(testcase_id, request, capability="cases")
    return await TestCaseService.delete(testcase_id)


@router.patch('/sort/{testcase_id}', dependencies=[Depends(bearer)])
async def update_sort(testcase_id: str, dto: TestCaseSortDto, request: Request):
    await _require_testcase_access(testcase_id, request, capability="cases")
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
    await _require_testcase_access(testcase_id, request, capability="traceability")
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
    await _require_testcase_access(testcase_id, request, capability="cases")
    case = await TestCaseService.restore_version(testcase_id, version_id, token)
    return await TestCaseService.serialize_case(case)


@router.post('/{testcase_id}/duplicate', dependencies=[Depends(bearer)])
async def duplicate_testcase(testcase_id: str, request: Request, token: str = Depends(bearer)):
    await _require_testcase_access(testcase_id, request, capability="cases")
    case = await TestCaseService.duplicate(testcase_id, token)
    return await TestCaseService.serialize_case(case)
