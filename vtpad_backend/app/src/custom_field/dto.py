import uuid
from pydantic import BaseModel
from typing import Optional, List, Any

from .model import CustomFieldType, CustomFieldEntityType


class CustomFieldCreateDto(BaseModel):
    name: str
    field_type: CustomFieldType
    entity_type: CustomFieldEntityType
    options: Optional[List[str]] = None
    required: bool = False
    sort: Optional[int] = 0
    space_id: str


class CustomFieldUpdateDto(BaseModel):
    name: Optional[str] = None
    field_type: Optional[CustomFieldType] = None
    options: Optional[List[str]] = None
    required: Optional[bool] = None
    sort: Optional[int] = None


class CustomFieldValueInput(BaseModel):
    field_id: str
    # The key is required, but explicit JSON null is a supported clear value.
    value: Any


class CustomFieldValueDto(BaseModel):
    field_id: str
    entity_id: str
    value: Any
