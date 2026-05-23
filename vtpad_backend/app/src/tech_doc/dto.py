from typing import Optional
from pydantic import BaseModel


class TechDocCreateDto(BaseModel):
    space_id: str
    title: str
    content: Optional[str] = None
    doc_type: Optional[str] = "other"
    source_url: Optional[str] = None
    version: Optional[str] = None
    parent_id: Optional[str] = None


class TechDocUpdateDto(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    doc_type: Optional[str] = None
    source_url: Optional[str] = None
    version: Optional[str] = None
    parent_id: Optional[str] = None


class TechDocSearchDto(BaseModel):
    space_id: str
    query: Optional[str] = None
    doc_type: Optional[str] = None
    page: int = 1
    page_size: int = 25
