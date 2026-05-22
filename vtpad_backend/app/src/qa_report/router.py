from fastapi import APIRouter, Depends
from .service import QAReportService
from ..common.crypto import bearer
from .dto import *
router = APIRouter(
    prefix='/qa-report',
    tags=['qa-report'],
    responses={404: {"message": "Not found"}},
)

service = QAReportService()


@router.get('/users', dependencies=[Depends(bearer)])
async def get_create_user_list(space_id: str):
    return await service.get_create_user_list(space_id)


@router.get('/bug-list', dependencies=[Depends(bearer)])
async def get_bugs_list(dto: GetBugsDto = Depends(GetBugsDto)):
    return await service.get_bugs_list(dto)
