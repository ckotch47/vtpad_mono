from fastapi import APIRouter, Depends, Request

from .service import SectionService
from .dto import *
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space
from ..test_suite.service import TestSuiteService

router = APIRouter(
    prefix='/v2/section',
    tags=['section'],
    responses={404: {"description": "Not found"}},
)


async def _require_section_capability(section_id: str, request: Request):
    section = await SectionService.get_by_id(section_id)
    suite = await TestSuiteService.get_by_id(str(section.suite_id))
    await check_user_into_space(str(suite.space_id), request, capability="sections")
    return section


@router.get('/suite/{suite_id}', dependencies=[Depends(bearer)])
async def get_by_suite(suite_id: str, request: Request):
    suite = await TestSuiteService.get_by_id(suite_id)
    await check_user_into_space(str(suite.space_id), request)
    return await SectionService.get_by_suite(suite_id)


@router.get('/suite/{suite_id}/tree', dependencies=[Depends(bearer)])
async def get_tree(suite_id: str, request: Request):
    suite = await TestSuiteService.get_by_id(suite_id)
    await check_user_into_space(str(suite.space_id), request)
    return await SectionService.get_tree(suite_id)


@router.get('/{section_id}', dependencies=[Depends(bearer)])
async def get_by_id(section_id: str, request: Request):
    section = await SectionService.get_by_id(section_id)
    suite = await TestSuiteService.get_by_id(str(section.suite_id))
    await check_user_into_space(str(suite.space_id), request)
    return section


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: SectionCreateDto, request: Request, token: str = Depends(bearer)):
    suite = await TestSuiteService.get_by_id(dto.suite_id)
    await check_user_into_space(str(suite.space_id), request, capability="sections")
    return await SectionService.create(dto, token)


@router.patch('/{section_id}', dependencies=[Depends(bearer)])
async def update(section_id: str, dto: SectionUpdateDto, request: Request):
    await _require_section_capability(section_id, request)
    return await SectionService.update(section_id, dto)


@router.delete('/{section_id}', dependencies=[Depends(bearer)])
async def delete(section_id: str, request: Request):
    await _require_section_capability(section_id, request)
    return await SectionService.delete(section_id)


@router.patch('/sort/{section_id}', dependencies=[Depends(bearer)])
async def update_sort(section_id: str, dto: SectionSortDto, request: Request):
    await _require_section_capability(section_id, request)
    return await SectionService.update_sort(section_id, dto, request)
