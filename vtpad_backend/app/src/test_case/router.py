from fastapi import APIRouter, Depends
from typing import Optional

from .service import TestCaseService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/test-case',
    tags=['test-case'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(space_id: str, type: Optional[str] = None):
    return await TestCaseService.get_by_space(space_id, type)


@router.get('/suite/{suite_id}', dependencies=[Depends(bearer)])
async def get_by_suite(suite_id: str):
    return await TestCaseService.get_by_suite(suite_id)


@router.get('/section/{section_id}', dependencies=[Depends(bearer)])
async def get_by_section(section_id: str):
    return await TestCaseService.get_by_section(section_id)


@router.get('/{testcase_id}', dependencies=[Depends(bearer)])
async def get_by_id(testcase_id: str):
    return await TestCaseService.get_by_id(testcase_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TestCaseCreateDto, token: str = Depends(bearer)):
    return await TestCaseService.create(dto, token)


@router.patch('/{testcase_id}', dependencies=[Depends(bearer)])
async def update(testcase_id: str, dto: TestCaseUpdateDto):
    return await TestCaseService.update(testcase_id, dto)


@router.delete('/{testcase_id}', dependencies=[Depends(bearer)])
async def delete(testcase_id: str):
    return await TestCaseService.delete(testcase_id)


@router.patch('/sort/{testcase_id}', dependencies=[Depends(bearer)])
async def update_sort(testcase_id: str, dto: TestCaseSortDto):
    return await TestCaseService.update_sort(testcase_id, dto)
