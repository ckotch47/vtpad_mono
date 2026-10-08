from pydantic import BaseModel, model_validator
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
    sort: Optional[int] = None


class SectionSortDto(BaseModel):
    sort_before_id: Optional[str] = None
    sort_after_id: Optional[str] = None

    @model_validator(mode='after')
    def require_one_neighbor(self):
        if (self.sort_before_id is None) == (self.sort_after_id is None):
            raise ValueError('Exactly one of sort_before_id or sort_after_id is required')
        return self
