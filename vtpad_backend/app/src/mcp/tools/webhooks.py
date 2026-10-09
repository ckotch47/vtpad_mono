from fastmcp.server.dependencies import get_http_request
from fastapi import HTTPException
from pydantic import ValidationError

from ..core import mcp
from ...webhook_integration.dto import MCPWebhookProcessDto, WebhookIntegrationCreateDto
from ...webhook_integration.service import (
    create_integration, process_webhook, read_integration,
    record_transport_failure, revoke_integration, rotate_integration,
)


@mcp.tool()
async def create_webhook_integration(payload: dict) -> dict:
    """Create a space-scoped CI webhook and return its random credential once."""
    return await create_integration(WebhookIntegrationCreateDto.model_validate(payload), get_http_request())


@mcp.tool()
async def get_webhook_integration(integration_id: str) -> dict:
    """Read safe webhook integration metadata; credentials are never returned."""
    return await read_integration(integration_id, get_http_request())


@mcp.tool()
async def rotate_webhook_integration_credential(integration_id: str) -> dict:
    """Atomically replace an integration credential and return the new one once."""
    return await rotate_integration(integration_id, get_http_request())


@mcp.tool()
async def revoke_webhook_integration(integration_id: str) -> dict:
    """Revoke a CI webhook integration."""
    return await revoke_integration(integration_id, get_http_request())


@mcp.tool()
async def process_webhook_event(payload: dict) -> dict:
    """Process the signed, bounded event through the same use case as HTTP callback."""
    try:
        dto = MCPWebhookProcessDto.model_validate(payload)
    except ValidationError:
        if isinstance(payload, dict) and payload.get('integration_id'):
            capped = await record_transport_failure(str(payload['integration_id']), 'invalid_mcp_envelope')
            if capped:
                raise HTTPException(status_code=429, detail='Webhook authentication rate limit exceeded') from None
        raise HTTPException(status_code=400, detail='Invalid webhook event envelope') from None
    return await process_webhook(
        str(dto.integration_id), dto.method, dto.path, dto.timestamp, dto.nonce,
        dto.idempotency_key, dto.signature, dto.body.encode('utf-8'),
    )
