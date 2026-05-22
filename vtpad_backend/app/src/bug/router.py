from typing import Any

from fastapi import APIRouter, Depends, BackgroundTasks

from .rto.get_filters_rto import GetFiltersRto
from ..common.crypto import bearer, user_payload
from .dto import *
from .rto import *
from .service import BugsService
from .enum import StateBugEnum
from ..common.right_guard import check_user_into_space
from ..tag.rto import GetTagRto

router = APIRouter(
    prefix="/v1/bugs",
    tags=["bugs"],
    responses={404: {"message": "Not found"}},
)
service = BugsService()
# TODO add guards for get or update by company
@router.post('', dependencies=[Depends(bearer)])
async def create_bug(bug: CreateBugDto, token: str = Depends(bearer),
                     background_tasks: BackgroundTasks = BackgroundTasks()):
    return await BugsService.create_bug(bug, user_payload(token), background_tasks)


@router.get('', dependencies=[Depends(bearer)], response_model=list[GetBugsWithFilterRto] | Any)
async def get_bugs(bug_filter: GetBugsDto = Depends(GetBugsDto)):
    return await BugsService.get_bugs_with_filter(bug_filter, )


@router.get('/detail/{bug_id}', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto)
async def get_bug_detail(bug_id: str):
    return await BugsService.get_bug_detail(bug_id)


@router.get('/detail-short', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto)
async def get_bug_detail_by_short_name(dto: GetBugDetailByShortNameDto = Depends(GetBugDetailByShortNameDto)):
    return await BugsService.get_bug_detail_by_short_name(dto.space_id, dto.short_name)


@router.get('/id/by-short', dependencies=[Depends(bearer)], response_model=str | None, deprecated=True)
async def get_id_by_short_name(dto: GetBugDetailByShortNameDto = Depends(GetBugDetailByShortNameDto)):
    return None # await BugsService.get_id_by_short_name(dto.space_id, dto.short_name)


@router.put('/{bug_id}', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto, deprecated=True)
async def update_bug(bug_id: str, dto: UpdateBugDto, token: str = Depends(bearer),
                     background_tasks: BackgroundTasks = BackgroundTasks()):
    return None # await BugsService.update_bug(dto, bug_id, user_payload(token), background_tasks)


@router.get('/filters', dependencies=[Depends(bearer)], response_model=GetFiltersRto | Any)
async def get_filter(space_id: str, token: str = Depends(bearer)):
    return await service.get_filters(space_id, user_payload(token))


@router.put('/{bug_id}/tag', dependencies=[Depends(bearer)], response_model=GetTagRto)
async def add_tag_to_bug(bug_id: str, dto: AddTagToBugDto):
    return await BugsService.add_tag_to_bug(bug_id, dto)


@router.delete('/{bug_id}/tag/{tag_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_tag_from_bug(bug_id: str, tag_id: str):
    return await BugsService.delete_tag_from_bug(bug_id, tag_id)


@router.get('/state-enum', dependencies=[Depends(bearer)], response_model=GetStateEnumRto)
async def get_state_enum_for_bugs():
    return {'state': StateBugEnum.get()}


router_v2 = APIRouter(
    prefix="/v2/bugs",
    tags=["bugs"],
    responses={404: {"message": "Not found"}},
)


@router_v2.patch('/{bug_id}', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto)
async def update_bug(bug_id: str, dto: UpdateBugDtoV2, token: str = Depends(bearer),
                     background_tasks: BackgroundTasks = BackgroundTasks()):
    return await BugsService.update_bug_v2(dto, bug_id, user_payload(token), background_tasks)


@router_v2.get('/filter-by-row/{space_id}/{row}', dependencies=[Depends(bearer),  Depends(check_user_into_space)])
async def get_filer_by_row(space_id: str, row: str):
    return await BugsService.get_filter_by_row(space_id, row)


@router_v2.get('/short/{short_name}', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto)
async def ge_detail_by_short_name(short_name: str, token: str = Depends(bearer)):
    return await BugsService.get_detail_by_short_name(short_name, user_payload(token))
