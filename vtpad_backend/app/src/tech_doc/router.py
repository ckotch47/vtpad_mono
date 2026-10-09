from typing import Optional
from fastapi import APIRouter, Depends, Request

from .service import TechDocService
from .dto import *
from ..common.crypto import bearer
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix='/v2/tech-doc',
    tags=['tech-doc'],
    responses={404: {"description": "Not found"}},
)


@router.get('/space/{space_id}/tree', dependencies=[Depends(bearer)])
async def get_tree(space_id: str, request: Request):
    await check_user_into_space(space_id, request)
    return await TechDocService.get_tree(space_id)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def get_by_space(
    space_id: str,
    request: Request,
    query: Optional[str] = None,
    doc_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 25,
):
    await check_user_into_space(space_id, request)
    return await TechDocService.get_by_space(space_id, query, doc_type, page, page_size)


@router.get('/{doc_id}', dependencies=[Depends(bearer)])
async def get_by_id(doc_id: str, request: Request):
    doc = await TechDocService.get_by_id(doc_id)
    await check_user_into_space(str(doc.space_id), request)
    return doc


@router.post('/', dependencies=[Depends(bearer)])
async def create(dto: TechDocCreateDto, request: Request):
    await check_user_into_space(dto.space_id, request, capability="tech_docs")
    return await TechDocService.create(dto)


@router.patch('/{doc_id}', dependencies=[Depends(bearer)])
async def update(doc_id: str, dto: TechDocUpdateDto, request: Request):
    doc = await TechDocService.get_by_id(doc_id)
    await check_user_into_space(str(doc.space_id), request, capability="tech_docs")
    return await TechDocService.update(doc_id, dto)


@router.delete('/{doc_id}', dependencies=[Depends(bearer)])
async def delete(doc_id: str, request: Request):
    doc = await TechDocService.get_by_id(doc_id)
    await check_user_into_space(str(doc.space_id), request, capability="tech_docs")
    return await TechDocService.delete(doc_id)
