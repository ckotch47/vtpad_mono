from typing import Any

from fastapi import APIRouter, Depends
from .dto import *
from .rto import *
from .service import TestCasesService
from ..common.crypto import bearer, user_payload
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix='/v1/testcases',
    tags=['testcases'],
    responses={404: {"message": "Not found"}},
)

service = TestCasesService()


@router.get('/filter/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)])
async def get_filter_for_testcase(space_id: str):
    return await service.get_filter_for_space(space_id)


@router.get('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[GetTestCaseListRto], description='sort: ASC or DESC')
async def get_testcases(space_id: str, dto: GetTestcaseDto = Depends(GetTestcaseDto)):
    return await service.get_test_case_list_by_space_id(space_id, dto)


@router.get('/paditem/{paditem_id}', dependencies=[Depends(bearer)], response_model=list[GetTestCaseListRto],deprecated=True)
async def get_testcase_py_pad_item(paditem_id: str):
    return await service.get_test_case_by_paditem_id(paditem_id)


@router.get('/detail/{testcase_id}', dependencies=[Depends(bearer)], response_model=GetTestCaseRto)
async def get_testcase_detail(testcase_id: str):
    return await service.get_test_cases_detail(testcase_id)


@router.get('/item/{item_id}', dependencies=[Depends(bearer)], response_model=list[GetTestCaseListRto] | list[GetTestCaseListForItem])
async def get_testcase_for_item_with_select(item_id: str, dto: GetTestcaseItemDto = Depends(GetTestcaseItemDto)):
    return await service.get_test_cases_for_item(item_id, dto)


@router.post('', dependencies=[Depends(bearer)], response_model=GetTestCaseRto)
async def create_testcase(dto: CreateTestCaseDto):
    return await service.create_test_case(dto)


@router.patch('/{testcase_id}', dependencies=[Depends(bearer)], response_model=GetTestCaseRto)
async def update_testcase(testcase_id: str, dto: UpdateTestCaseDto):
    return await service.update_test_case(dto, testcase_id)


@router.post('/image/{testcase_id}', dependencies=[Depends(bearer)], response_model=bool, deprecated=True)
async def add_image_to_testcase(testcase_id: str, dto: AddImageTestcaseDto):
    return await service.add_image(testcase_id, dto)


@router.delete('/image/{testcase_id}/{image_id}', dependencies=[Depends(bearer)], response_model=bool, deprecated=True)
async def delete_image_from_testcase(testcase_id: str, image_id: str):
    return await service.delete_image(testcase_id, image_id)


@router.delete('/{testcase_id}', dependencies=[Depends(bearer)], response_model=bool, )
async def delete_testcase(testcase_id: str):
    return await service.delete_test_case(testcase_id)


@router.delete('/paditem/{testcase_id}/{paditem_id}', dependencies=[Depends(bearer)], response_model=bool, deprecated=True)
async def delete_case_from_item(testcase_id: str, paditem_id: str):
    return await service.delete_case_from_paditem(testcase_id, paditem_id)

@router.get('/shortname/{short_name}', dependencies=[Depends(bearer)], response_model=GetTestCaseByShortName)
async def get_testcase_by_short_name(short_name: str, token: str = Depends(bearer)):
    return await service.get_case_by_short_name(short_name, user_payload(token))
