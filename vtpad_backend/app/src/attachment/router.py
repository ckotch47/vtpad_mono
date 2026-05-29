from fastapi import APIRouter, Depends

from .service import AttachmentService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/attachment',
    tags=['attachment'],
    responses={404: {"description": "Not found"}},
)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: AttachmentCreateDto, token: str = Depends(bearer)):
    return await AttachmentService.create(dto.entity_type, dto.entity_id, dto.file_id, token)


@router.get('/{entity_type}/{entity_id}', dependencies=[Depends(bearer)])
async def get_by_entity(entity_type: str, entity_id: str):
    return await AttachmentService.get_by_entity(entity_type, entity_id)


@router.delete('/{attachment_id}', dependencies=[Depends(bearer)])
async def delete(attachment_id: str):
    return await AttachmentService.delete(attachment_id)
