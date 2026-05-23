from fastapi import APIRouter, Depends

from .service import EnvironmentService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/environment',
    tags=['environment'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(space_id: str):
    return await EnvironmentService.get_by_space(space_id)


@router.get('/{env_id}', dependencies=[Depends(bearer)])
async def get_by_id(env_id: str):
    return await EnvironmentService.get_by_id(env_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: EnvironmentCreateDto, token: str = Depends(bearer)):
    return await EnvironmentService.create(dto, token)


@router.patch('/{env_id}', dependencies=[Depends(bearer)])
async def update(env_id: str, dto: EnvironmentUpdateDto):
    return await EnvironmentService.update(env_id, dto)


@router.delete('/{env_id}', dependencies=[Depends(bearer)])
async def delete(env_id: str):
    return await EnvironmentService.delete(env_id)
