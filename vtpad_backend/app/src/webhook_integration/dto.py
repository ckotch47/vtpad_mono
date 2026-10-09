from uuid import UUID

from pydantic import BaseModel, Field


class ResultMappingDto(BaseModel):
    external_id: str = Field(min_length=1, max_length=255)
    result_id: UUID


class WebhookIntegrationCreateDto(BaseModel):
    space_id: UUID
    name: str = Field(min_length=1, max_length=120)
    run_ids: list[UUID] = Field(min_length=1, max_length=1000)
    result_mappings: list[ResultMappingDto] = Field(min_length=1, max_length=10000)


class WebhookIntegrationReadDto(BaseModel):
    id: UUID


class WebhookBodyResultDto(BaseModel):
    external_id: str = Field(min_length=1, max_length=255)
    status: str
    duration_seconds: int | None = Field(default=None, ge=0)
    comment: str | None = Field(default=None, max_length=4000)


class WebhookBodyDto(BaseModel):
    results: list[WebhookBodyResultDto] = Field(min_length=1, max_length=1000)


class MCPWebhookProcessDto(BaseModel):
    integration_id: UUID
    method: str = Field(min_length=1, max_length=16)
    path: str = Field(min_length=1, max_length=512)
    timestamp: str = Field(min_length=1, max_length=12, pattern=r'^[0-9]{1,12}$')
    nonce: str = Field(min_length=16, max_length=128, pattern=r'^[\x20-\x7E]{16,128}$')
    idempotency_key: str = Field(min_length=1, max_length=128)
    signature: str = Field(min_length=64, max_length=64, pattern=r'^[0-9A-Fa-f]{64}$')
    body: str = Field(max_length=1024 * 1024)
