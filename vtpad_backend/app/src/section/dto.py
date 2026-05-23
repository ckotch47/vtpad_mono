from pydantic import BaseModel
from typing import Optional


class SectionCreateDto(BaseModel):
    name: str
    description: Optional[str] = None
    suite_id: str
    parent_id: Optional[str] = None


class SectionUpdateDto(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None


class SectionSortDto(BaseModel):
    sort_before_id: Optional[str] = None
    sort_after_id: Optional[str] = None
