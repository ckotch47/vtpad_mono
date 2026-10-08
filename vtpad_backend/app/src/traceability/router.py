from fastapi import APIRouter, Depends, Request

from .dto import TechDocTestCasesReplaceDto
from .service import TraceabilityService
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space


router = APIRouter(
    prefix='/v2/traceability',
    tags=['traceability'],
    responses={404: {'description': 'Not found'}},
)


async def _require_tech_doc_access(tech_doc_id: str, request: Request):
    from ..tech_doc.model import TechDocModel

    tech_doc = await TechDocModel.get_or_none(id=tech_doc_id)
    if not tech_doc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Tech doc not found')
    await check_user_into_space(str(tech_doc.space_id), request)
    return tech_doc


async def _require_testcase_access(testcase_id: str, request: Request):
    from ..test_case.model import TestCaseModel

    testcase = await TestCaseModel.get_or_none(id=testcase_id)
    if not testcase:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Test case not found')
    await check_user_into_space(str(testcase.space_id), request)
    return testcase

tech_doc_router = APIRouter(
    prefix='/v2/tech-doc',
    tags=['traceability'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/tech-doc/{tech_doc_id}/test-case/{testcase_id}', dependencies=[Depends(bearer)])
async def link_tech_doc_to_testcase(tech_doc_id: str, testcase_id: str, request: Request):
    await _require_tech_doc_access(tech_doc_id, request)
    await _require_testcase_access(testcase_id, request)
    return await TraceabilityService.link(tech_doc_id, testcase_id)


@router.delete('/tech-doc/{tech_doc_id}/test-case/{testcase_id}', dependencies=[Depends(bearer)])
async def unlink_tech_doc_from_testcase(tech_doc_id: str, testcase_id: str, request: Request):
    await _require_tech_doc_access(tech_doc_id, request)
    await _require_testcase_access(testcase_id, request)
    return await TraceabilityService.unlink(tech_doc_id, testcase_id)


@router.get('/tech-doc/{tech_doc_id}/test-cases', dependencies=[Depends(bearer)])
async def get_testcases_for_tech_doc(tech_doc_id: str, request: Request):
    await _require_tech_doc_access(tech_doc_id, request)
    return await TraceabilityService.get_testcases_for_doc(tech_doc_id)


@router.get('/test-case/{testcase_id}/tech-docs', dependencies=[Depends(bearer)])
async def get_tech_docs_for_testcase(testcase_id: str, request: Request):
    await _require_testcase_access(testcase_id, request)
    return await TraceabilityService.get_docs_for_testcase(testcase_id)


@tech_doc_router.get('/{tech_doc_id}/test-cases', dependencies=[Depends(bearer)])
async def get_test_cases_for_tech_doc(tech_doc_id: str, request: Request):
    await _require_tech_doc_access(tech_doc_id, request)
    return await TraceabilityService.get_testcases_for_doc(tech_doc_id)


@tech_doc_router.put('/{tech_doc_id}/test-cases', dependencies=[Depends(bearer)])
async def replace_test_cases_for_tech_doc(tech_doc_id: str, dto: TechDocTestCasesReplaceDto, request: Request):
    await _require_tech_doc_access(tech_doc_id, request)
    for testcase_id in dto.testcase_ids:
        await _require_testcase_access(testcase_id, request)
    return await TraceabilityService.replace_testcases_for_doc(tech_doc_id, dto.testcase_ids)
