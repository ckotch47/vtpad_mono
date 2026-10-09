from uuid import UUID

from fastapi import APIRouter, Depends, Request

from ..common.crypto import bearer
from .dto import EmailReportPreviewDto, EmailReportSendDto
from .service import EmailReportService

router = APIRouter(prefix='/qa-report/email', tags=['qa-report-email'])


@router.get('/recipients/{space_id}', dependencies=[Depends(bearer)])
async def get_recipients(space_id: UUID, request: Request):
    return await EmailReportService.get_recipients(space_id, request)


@router.post('/preview', dependencies=[Depends(bearer)])
async def create_preview(dto: EmailReportPreviewDto, request: Request):
    return await EmailReportService.create_preview(dto, request)


@router.post('/send', dependencies=[Depends(bearer)])
async def send_report(dto: EmailReportSendDto, request: Request):
    return await EmailReportService.send(dto, request)
