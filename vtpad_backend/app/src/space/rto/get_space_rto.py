import uuid

from pydantic import BaseModel
from typing import Any

from app.src.spacesuser.model import SpacesUserRole


class GetSpaceRto(BaseModel):
    id: str | uuid.UUID
    name: str
    role: SpacesUserRole | str | None = None
    sort: int | None = None
    short_name: str | None = None
