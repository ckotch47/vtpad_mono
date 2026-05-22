from fastapi import APIRouter, Depends, UploadFile

from .service import FileService
from ..common.crypto import bearer, user_payload

router = APIRouter(
    prefix="/v1/file",
    tags=["file"],
    responses={404: {"message": "Not found"}},
)


@router.post('', dependencies=[Depends(bearer)], description='upload and set user avatar')
async def create_upload_file(file: UploadFile, token: str = Depends(bearer)):
    return await FileService.save_file(file, user_payload(token))


@router.post('/image', dependencies=[Depends(bearer)])
async def create_upload_image(file: UploadFile):
    return await FileService.save_image(file)


@router.get('/{file_id}')
async def get_file(file_id: str):
    return await FileService.get_file(file_id)
