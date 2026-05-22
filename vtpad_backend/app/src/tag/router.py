from functools import wraps

from fastapi import APIRouter, Depends

from .rto import GetTagRto
from ..common.crypto import bearer, user_payload
from .dto import *
from .service import TagService
from ..common.right_guard import check_user_into_space
from ..spacesuser.service import SpacesUserService

router = APIRouter(
    prefix='/v1/tag',
    tags=['tag'],
    responses={404: {"message": "Not found"}},
)


def check_right_edit_tags(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await SpacesUserService.check_right_edit_tags(user_payload(kwargs.get('token')), kwargs.get('tag_id'))
        return await func(*args, **kwargs)

    return wrapper


def check_right_add_tags(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await SpacesUserService.check_right_add_tags(user_payload(kwargs.get('token')), kwargs.get('space_id'))
        return await func(*args, **kwargs)

    return wrapper


@router.get('/{space_id}', dependencies=[Depends(bearer),Depends(check_user_into_space) ], response_model=list[GetTagRto])
async def get_tags(space_id: str):
    return await TagService.get_tag(space_id)


@router.put('/{tag_id}', dependencies=[Depends(bearer)], response_model=GetTagRto)
@check_right_edit_tags
async def update_tag(tag_id: str, dto: UpdateTagDto, token: str = Depends(bearer)):
    return await TagService.update_tag(tag_id, dto)


@router.post('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=GetTagRto)
@check_right_add_tags
async def create_tag(space_id: str, dto: CreateTagDto, token: str = Depends(bearer)):
    return await TagService.create_tag(space_id, dto)


@router.delete('/{tag_id}', dependencies=[Depends(bearer)], response_model=bool)
@check_right_edit_tags
async def delete_tag(tag_id: str, token: str = Depends(bearer)):
    return await TagService.delete_tag(tag_id)
