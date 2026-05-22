from functools import wraps

from fastapi import APIRouter, Depends
from .service import PadService
from .dto import *
from .rto import *
from ..common.crypto import bearer, user_payload
from ..common.right_guard import check_user_into_space
from ..spacesuser.service import SpacesUserService

router = APIRouter(
    prefix='/v1/pad',
    tags=['pad'],
    responses={404: {"message": "Not found"}},
)


def check_right_edit_pad(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await SpacesUserService.check_right_edit_pad(user_payload(kwargs.get('token')), kwargs.get('pad_id'))
        return await func(*args, **kwargs)

    return wrapper


@router.get('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[PadRto])
async def get_pad(space_id: str, folderId: str = None):
    return await PadService.get_pad(space_id, folderId)


@router.get('/detail/{pad_id}', dependencies=[Depends(bearer)], response_model=PadRto)
async def get_pad_detail(pad_id: str):
    return await PadService.get_pad_detail(pad_id)


@router.post('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=PadRto)
async def create_pad(space_id: str, item: CreatePadDto):
    return await PadService.create_pad(space_id, item)


@router.patch('/{pad_id}', dependencies=[Depends(bearer)], response_model=PadRto)
@check_right_edit_pad
async def update_pad(pad_id: str, item: UpdatePadDto, token: str = Depends(bearer)):
    return await PadService.update_pad(pad_id, item)


@router.delete('/{pad_id}', dependencies=[Depends(bearer)], response_model=bool)
@check_right_edit_pad
async def delete_pad(pad_id: str, token: str = Depends(bearer)):
    return await PadService.delete_pad(pad_id)


@router.patch('/sort/{pad_id}', dependencies=[Depends(bearer)], response_model=list[PadRto])
@check_right_edit_pad
async def update_sort_pad(pad_id: str, dto: UpdateSortPadDto, token: str = Depends(bearer)):
    return await PadService.update_sort_pad(pad_id, dto)
