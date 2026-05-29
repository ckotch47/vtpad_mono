import uuid
from pydantic import BaseModel
from typing import Optional, List, Any

from .model import CustomFieldType, CustomFieldEntityType


class CustomFieldCreateDto(BaseModel):
    name: str
    field_type: CustomFieldType
    entity_type: CustomFieldEntityType
    options: Optional[List[str]] = None
    sort: Optional[int] = 0
    space_id: str


class CustomFieldUpdateDto(BaseModel):
    name: Optional[str] = None
    field_type: Optional[CustomFieldType] = None
    options: Optional[List[str]] = None
    sort: Optional[int] = None


class CustomFieldValueDto(BaseModel):
    field_id: str
    entity_id: str
    value: Any
