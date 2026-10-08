from pydantic import BaseModel
from pydantic import Field, field_validator
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
    priority: str = "P2"
    tags: List[str] = Field(default_factory=list)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        if value not in {"P0", "P1", "P2", "P3"}:
            raise ValueError("priority must be P0, P1, P2, or P3")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, values: List[str]) -> List[str]:
        if len(values) > 50:
            raise ValueError("at most 50 tags are allowed")
        if any(not isinstance(value, str) or not value.strip() or len(value.strip()) > 255 for value in values):
            raise ValueError("tag names must contain 1 to 255 characters")
        return values


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
    priority: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in {"P0", "P1", "P2", "P3"}:
            raise ValueError("priority must be P0, P1, P2, or P3")
        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, values: Optional[List[str]]) -> Optional[List[str]]:
        if values is not None:
            if len(values) > 50:
                raise ValueError("at most 50 tags are allowed")
            if any(not isinstance(value, str) or not value.strip() or len(value.strip()) > 255 for value in values):
                raise ValueError("tag names must contain 1 to 255 characters")
        return values


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
