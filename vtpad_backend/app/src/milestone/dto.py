from pydantic import BaseModel
from typing import Optional
from datetime import date


class MilestoneCreateDto(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    space_id: str


class MilestoneUpdateDto(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
