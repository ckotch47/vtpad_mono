from pydantic import BaseModel


class AttachmentCreateDto(BaseModel):
    entity_type: str
    entity_id: str
    file_id: str
