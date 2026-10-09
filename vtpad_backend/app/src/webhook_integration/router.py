from fastapi import APIRouter, Depends, HTTPException, Request

from ..common.crypto import bearer
from .dto import WebhookIntegrationCreateDto
from .service import (
    MAX_BODY_BYTES,
    create_integration, process_webhook, read_integration,
    record_transport_failure, revoke_integration, rotate_integration,
)

router = APIRouter(prefix='/v2/webhooks', tags=['webhooks'])


@router.post('/integrations', dependencies=[Depends(bearer)])
async def create(dto: WebhookIntegrationCreateDto, request: Request):
    return await create_integration(dto, request)


@router.get('/integrations/{integration_id}', dependencies=[Depends(bearer)])
async def read(integration_id: str, request: Request):
    return await read_integration(integration_id, request)


@router.post('/integrations/{integration_id}/rotate', dependencies=[Depends(bearer)])
async def rotate(integration_id: str, request: Request):
    return await rotate_integration(integration_id, request)


@router.post('/integrations/{integration_id}/revoke', dependencies=[Depends(bearer)])
async def revoke(integration_id: str, request: Request):
    return await revoke_integration(integration_id, request)


@router.post('/integrations/{integration_id}/callback')
async def callback(integration_id: str, request: Request):
    chunks = []
    total_bytes = 0
    async for chunk in request.stream():
        total_bytes += len(chunk)
        if total_bytes > MAX_BODY_BYTES:
            capped = await record_transport_failure(integration_id, 'payload_too_large')
            raise HTTPException(
                status_code=429 if capped else 413,
                detail='Webhook authentication rate limit exceeded' if capped else 'Webhook payload exceeds 1 MiB',
            )
        chunks.append(chunk)
    body = b''.join(chunks)
    response = await process_webhook(
        integration_id, request.method, request.url.path,
        request.headers.get('x-vtpad-timestamp', ''),
        request.headers.get('x-vtpad-nonce', ''),
        request.headers.get('idempotency-key', ''),
        request.headers.get('x-vtpad-signature', ''), body,
    )
    return response
