from pydantic import BaseModel, Field
from typing import Optional


class TestSuiteCreateDto(BaseModel):
    name: str
    description: Optional[str] = None
    space_id: str


class TestSuiteUpdateDto(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TestSuiteSortDto(BaseModel):
    sort_before_id: Optional[str] = None
    sort_after_id: Optional[str] = None
