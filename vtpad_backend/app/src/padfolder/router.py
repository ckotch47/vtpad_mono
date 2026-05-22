from fastapi import APIRouter, Depends
from ..common.crypto import bearer, user_payload
from .service import PadFolderService
from .dto import *
from .rto import *
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix='/v1/pad-folder',
    tags=['pad-folder'],
    responses={404: {"message": "Not found"}},
)


@router.get('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[PadFolderRto])
async def get_folders(space_id: str):
    return await PadFolderService.get_folders_for_space(space_id)


@router.get('/detail/{folder_id}', dependencies=[Depends(bearer)], response_model=GetFolderDetailRto)
async def get_folder_detail(folder_id: str):
    return await PadFolderService.get_folder_detail(folder_id)


@router.post('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=PadFolderRto)
async def create_folder(space_id: str, dto: CreatePadFolderDto, token: str = Depends(bearer)):
    await PadFolderService.check_right_edit_folder(space_id=space_id, user_payload=user_payload(token))
    return await PadFolderService.create_folder(space_id, dto)


@router.patch('/{folder_id}', dependencies=[Depends(bearer)], response_model=GetFolderDetailRto)
async def update_folder(folder_id: str, dto: UpdatePadFolderDto, token: str = Depends(bearer)):
    await PadFolderService.check_right_edit_folder(folder_id=folder_id, user_payload=user_payload(token))
    return await PadFolderService.update_folder(folder_id, dto)


@router.delete('/{folder_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_folder(folder_id: str, token: str = Depends(bearer)):
    await PadFolderService.check_right_edit_folder(folder_id=folder_id, user_payload=user_payload(token))
    return await PadFolderService.delete_folder(folder_id)

