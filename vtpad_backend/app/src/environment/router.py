from fastapi import APIRouter, Depends, Request

from .service import EnvironmentService
from .dto import *
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix='/v2/environment',
    tags=['environment'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(space_id: str, request: Request):
    await check_user_into_space(space_id, request)
    return await EnvironmentService.get_by_space(space_id)


@router.get('/{env_id}', dependencies=[Depends(bearer)])
async def get_by_id(env_id: str, request: Request):
    environment = await EnvironmentService.get_by_id(env_id)
    await check_user_into_space(str(environment.space_id), request)
    return environment


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: EnvironmentCreateDto, request: Request, token: str = Depends(bearer)):
    await check_user_into_space(str(dto.space_id), request, capability="runs")
    return await EnvironmentService.create(dto, token)


@router.patch('/{env_id}', dependencies=[Depends(bearer)])
async def update(env_id: str, dto: EnvironmentUpdateDto, request: Request):
    environment = await EnvironmentService.get_by_id(env_id)
    await check_user_into_space(str(environment.space_id), request, capability="runs")
    return await EnvironmentService.update(env_id, dto)


@router.delete('/{env_id}', dependencies=[Depends(bearer)])
async def delete(env_id: str, request: Request):
    environment = await EnvironmentService.get_by_id(env_id)
    await check_user_into_space(str(environment.space_id), request, capability="runs")
    return await EnvironmentService.delete(env_id)
