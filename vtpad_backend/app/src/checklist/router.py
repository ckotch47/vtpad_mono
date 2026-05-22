from fastapi import APIRouter, Depends, BackgroundTasks

from app.src.common.crypto import bearer, user_payload
from .dto import *
from .rto import *

from .service import ChecklistService
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix="/v1/checklist",
    tags=["checklist"],
    responses={404: {"message": "Not found"}},
)

service = ChecklistService()

@router.get('/list/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[ChecklistRto])
async def get_list_checklists(space_id: str, dto: GetChecklistDto = Depends(GetChecklistDto)):
    return await service.get_checklist_list(space_id, dto)


@router.get('/{checklist_id}', dependencies=[Depends(bearer)], response_model=ChecklistRto)
async def get_checklist_detail(checklist_id: str, token: str = Depends(bearer)):
    await service.check_user_into_space_by_checklist_id(user_payload(token), checklist_id)
    return await service.get_checklist_detail_by_id(checklist_id)

@router.post('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=ChecklistRto)
async def create_checklist(space_id: str, dto: CreateChecklistDto):
    return await service.create_checklist(space_id, dto)

@router.patch('/{checklist_id}', dependencies=[Depends(bearer)], response_model=ChecklistRto)
async def update_checklist(checklist_id: str, dto: CreateChecklistDto, token: str = Depends(bearer)):
    await service.check_user_into_space_by_checklist_id(user_payload(token), checklist_id)
    return await service.update_checklist(checklist_id, dto)

@router.delete('/{checklist_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_checklist(checklist_id: str, token: str = Depends(bearer)):
    await service.check_user_into_space_by_checklist_id(user_payload(token), checklist_id)
    return await service.delete_checklist_by_id(checklist_id)


@router.get('/by-short/{short_name}', dependencies=[Depends(bearer)], response_model=GetByShortName)
async def get_checklist_by_short_name(short_name: str, token: str = Depends(bearer)):
    return await service.get_checklist_by_short_name(short_name, user_payload(token))