from pydantic import BaseModel
from typing import Optional, Dict, Any


class TestPlanCreateDto(BaseModel):
    name: str
    description: Optional[str] = None
    space_id: str
    suite_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class TestPlanUpdateDto(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    suite_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
