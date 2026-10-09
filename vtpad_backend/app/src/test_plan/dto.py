from pydantic import BaseModel, Field
from typing import Any, Optional, List


class TestPlanCustomFieldFilterDto(BaseModel):
    field_id: str
    value: Any


class TestPlanFiltersDto(BaseModel):
    priorities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    custom_fields: List[TestPlanCustomFieldFilterDto] = Field(default_factory=list)


class TestPlanPreviewDto(BaseModel):
    space_id: str
    suite_ids: List[str] = Field(default_factory=list)
    case_ids: List[str] = Field(default_factory=list)
    filters: TestPlanFiltersDto = Field(default_factory=TestPlanFiltersDto)


class TestPlanCreateDto(BaseModel):
    name: str
    description: Optional[str] = None
    space_id: str
    suite_ids: Optional[List[str]] = None
    case_ids: Optional[List[str]] = None
    filters: TestPlanFiltersDto = Field(default_factory=TestPlanFiltersDto)


class TestPlanUpdateDto(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    suite_ids: Optional[List[str]] = None
    case_ids: Optional[List[str]] = None
    filters: Optional[TestPlanFiltersDto] = None
