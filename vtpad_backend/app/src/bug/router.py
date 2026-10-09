from typing import Any

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request

from .rto.get_filters_rto import GetFiltersRto
from ..common.crypto import bearer, user_payload
from .dto import *
from .rto import *
from .service import BugsService
from .enum import StateBugEnum
from ..common.right_guard import check_user_into_space
from ..tag.rto import GetTagRto
from ..tag.model import TagModel

router = APIRouter(
    prefix="/v1/bugs",
    tags=["bugs"],
    responses={404: {"message": "Not found"}},
)
service = BugsService()


async def _require_bug_write(bug_id: str, request: Request, capability: str = "bugs"):
    bug = await BugsService._get_bug_or_404(bug_id)
    await check_user_into_space(str(bug.spaces_id), request, capability=capability)
    return bug


async def _require_bug_tag_write(bug_id: str, request: Request):
    bug = await _require_bug_write(bug_id, request)
    await check_user_into_space(str(bug.spaces_id), request, capability="tags")
    return bug


async def _validate_bug_tag_pair(bug_id: str, tag_id: str, request: Request):
    bug = await _require_bug_tag_write(bug_id, request)
    tag = await TagModel.get_or_none(id=tag_id)
    if tag is None or str(tag.space_id) != str(bug.spaces_id):
        raise HTTPException(status_code=404, detail="Tag not found in bug space")
    return bug


# TODO add guards for get or update by company
@router.post('', dependencies=[Depends(bearer)])
async def create_bug(bug: CreateBugDto, request: Request, token: str = Depends(bearer),
                     background_tasks: BackgroundTasks = BackgroundTasks()):
    await check_user_into_space(str(bug.space_id), request, capability="bugs")
    return await BugsService.create_bug(bug, user_payload(token), background_tasks)


@router.get('', dependencies=[Depends(bearer)], response_model=list[GetBugsWithFilterRto] | Any)
async def get_bugs(bug_filter: GetBugsDto = Depends(GetBugsDto)):
    return await BugsService.get_bugs_with_filter(bug_filter, )


@router.get('/detail/{bug_id}', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto)
async def get_bug_detail(bug_id: str):
    return await BugsService.get_bug_detail(bug_id)


@router.put('/{bug_id}', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto, deprecated=True)
async def update_bug(bug_id: str, dto: UpdateBugDto, request: Request, token: str = Depends(bearer),
                     background_tasks: BackgroundTasks = BackgroundTasks()):
    await _require_bug_write(bug_id, request)
    return await BugsService.update_bug(dto, bug_id, user_payload(token), background_tasks)


@router.get('/filters', dependencies=[Depends(bearer)], response_model=GetFiltersRto | Any)
async def get_filter(space_id: str, token: str = Depends(bearer)):
    return await service.get_filters(space_id, user_payload(token))


@router.put('/{bug_id}/tag', dependencies=[Depends(bearer)], response_model=GetTagRto)
async def add_tag_to_bug(bug_id: str, dto: AddTagToBugDto, request: Request):
    await _validate_bug_tag_pair(bug_id, dto.tag_id, request)
    return await BugsService.add_tag_to_bug(bug_id, dto)


@router.delete('/{bug_id}/tag/{tag_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_tag_from_bug(bug_id: str, tag_id: str, request: Request):
    await _validate_bug_tag_pair(bug_id, tag_id, request)
    return await BugsService.delete_tag_from_bug(bug_id, tag_id)


@router.get('/state-enum', dependencies=[Depends(bearer)], response_model=GetStateEnumRto)
async def get_state_enum_for_bugs():
    return {'state': StateBugEnum.get()}


router_v2 = APIRouter(
    prefix="/v2/bugs",
    tags=["bugs"],
    responses={404: {"message": "Not found"}},
)


@router_v2.get('/space/{space_id}/by-link/{link_uuid}', dependencies=[Depends(bearer), Depends(check_user_into_space)])
async def get_bug_by_link_uuid(space_id: str, link_uuid: str):
    return await BugsService.get_bug_detail_by_link_uuid(link_uuid, space_id)


@router_v2.patch('/{bug_id}', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto)
async def update_bug(bug_id: str, dto: UpdateBugDtoV2, request: Request, token: str = Depends(bearer),
                     background_tasks: BackgroundTasks = BackgroundTasks()):
    bug = await _require_bug_write(bug_id, request)
    if dto.tags is not None:
        await check_user_into_space(str(bug.spaces_id), request, capability="tags")
        tag_ids = list(dict.fromkeys(dto.tags))
        tags = await TagModel.filter(id__in=tag_ids, space_id=bug.spaces_id)
        if len(tags) != len(tag_ids):
            raise HTTPException(status_code=422, detail="Every bug tag must belong to the bug space")
    return await BugsService.update_bug_v2(dto, bug_id, user_payload(token), background_tasks)


@router_v2.get('/filter-by-row/{space_id}/{row}', dependencies=[Depends(bearer),  Depends(check_user_into_space)])
async def get_filer_by_row(space_id: str, row: str):
    return await BugsService.get_filter_by_row(space_id, row)


@router_v2.get('/short/{short_name}', dependencies=[Depends(bearer)], response_model=GetBugsWithFilterRto)
async def ge_detail_by_short_name(short_name: str, token: str = Depends(bearer)):
    return await BugsService.get_detail_by_short_name(short_name, user_payload(token))
