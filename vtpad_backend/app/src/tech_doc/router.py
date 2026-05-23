from typing import Optional
from fastapi import APIRouter, Depends

from .service import TechDocService
from .dto import *
from ..common.crypto import bearer

router = APIRouter(
    prefix='/v2/tech-doc',
    tags=['tech-doc'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}/tree', dependencies=[Depends(bearer)])
async def get_tree(space_id: str):
    return await TechDocService.get_tree(space_id)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(
    space_id: str,
    query: Optional[str] = None,
    doc_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
):
    return await TechDocService.get_by_space(space_id, query, doc_type, page, page_size)


@router.get('/{doc_id}', dependencies=[Depends(bearer)])
async def get_by_id(doc_id: str):
    return await TechDocService.get_by_id(doc_id)


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TechDocCreateDto):
    return await TechDocService.create(dto)


@router.patch('/{doc_id}', dependencies=[Depends(bearer)])
async def update(doc_id: str, dto: TechDocUpdateDto):
    return await TechDocService.update(doc_id, dto)


@router.delete('/{doc_id}', dependencies=[Depends(bearer)])
async def delete(doc_id: str):
    return await TechDocService.delete(doc_id)
