from fastapi import APIRouter, Depends, HTTPException, Request

from .rto import GetTagRto
from ..common.crypto import bearer
from .dto import *
from .service import TagService
from ..common.right_guard import check_user_into_space
from .model import TagModel

router = APIRouter(
    prefix='/v1/tag',
    tags=['tag'],
    responses={404: {"message": "Not found"}},
)


async def _require_tag_write(tag_id: str, request: Request):
    tag = await TagModel.get_or_none(id=tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    await check_user_into_space(str(tag.space_id), request, capability="tags")
    return tag


@router.get('/{space_id}', dependencies=[Depends(bearer),Depends(check_user_into_space) ], response_model=list[GetTagRto])
async def get_tags(space_id: str):
    return await TagService.get_tag(space_id)


@router.put('/{tag_id}', dependencies=[Depends(bearer)], response_model=GetTagRto)
async def update_tag(tag_id: str, dto: UpdateTagDto, request: Request):
    await _require_tag_write(tag_id, request)
    return await TagService.update_tag(tag_id, dto)


@router.post('/{space_id}', dependencies=[Depends(bearer)], response_model=GetTagRto)
async def create_tag(space_id: str, dto: CreateTagDto, request: Request):
    await check_user_into_space(space_id, request, capability="tags")
    return await TagService.create_tag(space_id, dto)


@router.delete('/{tag_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_tag(tag_id: str, request: Request):
    await _require_tag_write(tag_id, request)
    return await TagService.delete_tag(tag_id)
