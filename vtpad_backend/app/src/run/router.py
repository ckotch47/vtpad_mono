from typing import Any

from fastapi import APIRouter, Depends
from .service import RunService
from .dto import *
from .rto import *
from ..common.crypto import bearer, user_payload
from ..common.right_guard import check_user_into_space
from ..spacesuser.service import SpacesUserService

router = APIRouter(
    prefix="/v1/runs",
    tags=["runs"],
    responses={404: {"message": "Not found"}},
)


@router.post('/{pad_id}', dependencies=[Depends(bearer)], response_model=RunRto)
async def create_run(pad_id: str, run: CreateRunDto, token: str = Depends(bearer)):
    await SpacesUserService.check_right_edit_pad(user_payload(token), pad_id)
    return await RunService.create_run(pad_id, run)


@router.delete('/{run_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_run(run_id: str, token: str = Depends(bearer)):
    await SpacesUserService.check_right_runs(user_payload(token), run_id)
    return await RunService.delete_run(run_id)


@router.get('/items/{run_id}', dependencies=[Depends(bearer)], response_model=list[GetItemsForRunRto] | Any)
async def get_items_fro_run(run_id: str):
    return await RunService.get_items_for_run(run_id)


@router.get('/{run_id}', dependencies=[Depends(bearer)], response_model=RunRto)
async def get_run(run_id: str):
    return await RunService.get_run(run_id)


@router.get('/all/{pad_id}', dependencies=[Depends(bearer)], response_model=list[RunRto])
async def get_all_run(pad_id: str):
    return await RunService.get_all_run(pad_id)


@router.get('/filter/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[GetFilterForRunRto])
async def get_filter_for_run_by_space(space_id: str):
    return await RunService.get_filter_for_run(space_id)


@router.get('/by-filter/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[GetRunsWithFilterRto])
async def get_runs_by_filter(dto: GetRunsDto = Depends(GetRunsDto)):
    return await RunService.get_runs_with_filter(dto)


@router.patch('/{run_id}', dependencies=[Depends(bearer)], response_model=bool)
async def update_run(run_id: str, name: str, token: str = Depends(bearer)):
    await SpacesUserService.check_right_runs(user_payload(token), run_id)
    return await RunService.update_run(run_id, name)


routerV2 = APIRouter(
    prefix="/v2/runs",
    tags=["runs"],
    responses={404: {"message": "Not found"}},
)


@routerV2.get('/last/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)])
async def get_last_run(space_id: str):
    return await RunService.get_last_run(space_id)

@routerV2.post('/{run_id}/rerun', dependencies=[Depends(bearer)], response_model=bool)
async def rerun_run(run_id: str):
    return await RunService.re_run_run_by_id(run_id)
