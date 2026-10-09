from fastapi import APIRouter, Depends, Request

from .service import CustomFieldService, CustomFieldValueService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/custom-field',
    tags=['custom-field'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(space_id: str, request: Request, entity_type: str = None):
    return await CustomFieldService.get_by_space(space_id, entity_type, request)


@router.get('/{field_id}', dependencies=[Depends(bearer)])
async def get_by_id(field_id: str, request: Request):
    return await CustomFieldService.get_by_id(field_id, request)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: CustomFieldCreateDto, request: Request, token: str = Depends(bearer)):
    return await CustomFieldService.create(dto, token, request)


@router.patch('/{field_id}', dependencies=[Depends(bearer)])
async def update(field_id: str, dto: CustomFieldUpdateDto, request: Request):
    return await CustomFieldService.update(field_id, dto, request)


@router.delete('/{field_id}', dependencies=[Depends(bearer)])
async def delete(field_id: str, request: Request):
    return await CustomFieldService.delete(field_id, request)


# Values
@router.post('/value', dependencies=[Depends(bearer)])
async def set_value(dto: CustomFieldValueDto, request: Request, token: str = Depends(bearer)):
    return await CustomFieldValueService.set_value(dto, request, token)


@router.get('/value/{entity_id}', dependencies=[Depends(bearer)])
async def get_values(entity_id: str, request: Request):
    return await CustomFieldValueService.get_values(entity_id, request)
