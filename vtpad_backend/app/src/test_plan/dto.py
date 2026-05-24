from pydantic import BaseModel
from typing import Optional, List


class TestPlanCreateDto(BaseModel):
    name: str
    description: Optional[str] = None
    space_id: str
    case_ids: Optional[List[str]] = None


class TestPlanUpdateDto(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    case_ids: Optional[List[str]] = None
