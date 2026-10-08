from pydantic import BaseModel
from pydantic import Field
from typing import List, Optional


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
    estimated_duration_seconds: Optional[int] = Field(default=None, ge=0)


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
    estimated_duration_seconds: Optional[int] = Field(default=None, ge=0)
    sort: Optional[int] = None


class TestCaseMoveDto(BaseModel):
    """Explicit destination for moving a case between suite locations."""

    suite_id: str
    # Required but nullable: null selects the suite's virtual Default section.
    section_id: Optional[str] = Field(...)


class TestCaseSortDto(BaseModel):
    sort_before_id: Optional[str] = None
    sort_after_id: Optional[str] = None


class TestCaseTechDocsReplaceDto(BaseModel):
    tech_doc_ids: List[str]
