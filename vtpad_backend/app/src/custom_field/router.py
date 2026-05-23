from fastapi import APIRouter, Depends

from .service import CustomFieldService, CustomFieldValueService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/custom-field',
    tags=['custom-field'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(space_id: str, entity_type: str = None):
    return await CustomFieldService.get_by_space(space_id, entity_type)


@router.get('/{field_id}', dependencies=[Depends(bearer)])
async def get_by_id(field_id: str):
    return await CustomFieldService.get_by_id(field_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: CustomFieldCreateDto, token: str = Depends(bearer)):
    return await CustomFieldService.create(dto, token)


@router.patch('/{field_id}', dependencies=[Depends(bearer)])
async def update(field_id: str, dto: CustomFieldUpdateDto):
    return await CustomFieldService.update(field_id, dto)


@router.delete('/{field_id}', dependencies=[Depends(bearer)])
async def delete(field_id: str):
    return await CustomFieldService.delete(field_id)


# Values
@router.post('/value', dependencies=[Depends(bearer)])
async def set_value(dto: CustomFieldValueDto):
    return await CustomFieldValueService.set_value(dto)


@router.get('/value/{entity_id}', dependencies=[Depends(bearer)])
async def get_values(entity_id: str):
    return await CustomFieldValueService.get_values(entity_id)
