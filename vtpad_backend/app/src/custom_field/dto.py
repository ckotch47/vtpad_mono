from pydantic import BaseModel
from typing import Optional, List, Any


class CustomFieldCreateDto(BaseModel):
    name: str
    field_type: str
    entity_type: str
    options: Optional[List[str]] = None
    sort: Optional[int] = 0
    space_id: str


class CustomFieldUpdateDto(BaseModel):
    name: Optional[str] = None
    field_type: Optional[str] = None
    options: Optional[List[str]] = None
    sort: Optional[int] = None


class CustomFieldValueDto(BaseModel):
    field_id: str
    entity_id: str
    value: Any
