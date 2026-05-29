from pydantic import BaseModel
from typing import Optional


class TestCaseCreateDto(BaseModel):
    title: str
    text: Optional[str] = None
    steps: Optional[str] = None
    expected_results: Optional[str] = None
    preconditions: Optional[str] = None
    postconditions: Optional[str] = None
    type: str = "manual"
    space_id: str
    suite_id: Optional[str] = None
    section_id: Optional[str] = None
    short_name: Optional[str] = None
    link: Optional[str] = None
    external_id: Optional[str] = None


class TestCaseUpdateDto(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    steps: Optional[str] = None
    expected_results: Optional[str] = None
    preconditions: Optional[str] = None
    postconditions: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    suite_id: Optional[str] = None
    section_id: Optional[str] = None
    short_name: Optional[str] = None
    link: Optional[str] = None
    external_id: Optional[str] = None
    sort: Optional[int] = None


class TestCaseSortDto(BaseModel):
    sort_before_id: Optional[str] = None
    sort_after_id: Optional[str] = None
