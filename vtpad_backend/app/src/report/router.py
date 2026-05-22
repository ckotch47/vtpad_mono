import uuid

from fastapi import APIRouter, Depends
from tortoise import Tortoise

from .service import ReportService, ReportServiceV2
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space
from .rto import *
router = APIRouter(
    prefix='/v1/report',
    tags=['report'],
    responses={404: {"message": "Not found"}},
)

service = ReportService()


@router.get('/test/list/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)])
async def get_test_list(space_id: str):
    return await service.get_test_list(space_id)


@router.get('/test/detail/{test_id}', dependencies=[Depends(bearer)])
async def get_test_detail(test_id: str):
    return await service.get_test_detail(test_id)


routerV2 = APIRouter(
    prefix='/v2/report',
    tags=['report'],
    responses={404: {"message": "Not found"}},
)
serviceV2 = ReportServiceV2()


@routerV2.get('/{space_id}/test/list',
              dependencies=[Depends(bearer), Depends(check_user_into_space)],
              response_model=list[GetTestListRto])
async def get_test_suite_list(space_id: uuid.UUID):
    return await serviceV2.get_test_list(space_id)


@routerV2.get('/{space_id}/test/{test_id}/detail',
              dependencies=[Depends(bearer), Depends(check_user_into_space)],
              response_model=GetTestDetailRto)
async def get_test_detail(space_id: str, test_id: str):
    return await serviceV2.get_test_detail(space_id, test_id)


@routerV2.get('/{space_id}/test/{test_id}/suite/list',
              dependencies=[Depends(bearer), Depends(check_user_into_space)],
              response_model=list[SuiteRto])
async def get_test_suite_list(space_id: str, test_id: str):
    return await serviceV2.get_suite_list(test_id)


@routerV2.get('/{space_id}/test/suite/{suite_id}/detail',
              dependencies=[Depends(bearer), Depends(check_user_into_space)],
              response_model=list[TestCaseRto])
async def get_detail_suite(space_id: str, suite_id: str):
    return await serviceV2.get_suite_detail(suite_id)
