from fastapi import APIRouter, Depends

from .service import SectionService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/section',
    tags=['section'],
    responses={404: {"description": "Not found"}},
)


@router.get('/suite/{suite_id}', dependencies=[Depends(bearer)])
async def get_by_suite(suite_id: str):
    return await SectionService.get_by_suite(suite_id)


@router.get('/suite/{suite_id}/tree', dependencies=[Depends(bearer)])
async def get_tree(suite_id: str):
    return await SectionService.get_tree(suite_id)


@router.get('/{section_id}', dependencies=[Depends(bearer)])
async def get_by_id(section_id: str):
    return await SectionService.get_by_id(section_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: SectionCreateDto, token: str = Depends(bearer)):
    return await SectionService.create(dto, token)


@router.patch('/{section_id}', dependencies=[Depends(bearer)])
async def update(section_id: str, dto: SectionUpdateDto):
    return await SectionService.update(section_id, dto)


@router.delete('/{section_id}', dependencies=[Depends(bearer)])
async def delete(section_id: str):
    return await SectionService.delete(section_id)


@router.patch('/sort/{section_id}', dependencies=[Depends(bearer)])
async def update_sort(section_id: str, dto: SectionSortDto):
    return await SectionService.update_sort(section_id, dto)
