from pydantic import BaseModel
from typing import Optional, Dict


class EnvironmentCreateDto(BaseModel):
    name: str
    os: Optional[str] = None
    browser: Optional[str] = None
    url: Optional[str] = None
    variables: Optional[Dict] = None
    space_id: str


class EnvironmentUpdateDto(BaseModel):
    name: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None
    url: Optional[str] = None
    variables: Optional[Dict] = None
