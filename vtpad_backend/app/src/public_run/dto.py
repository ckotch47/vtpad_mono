from uuid import UUID

from pydantic import BaseModel


class PublicRunLinkCreateDto(BaseModel):
    run_id: UUID
