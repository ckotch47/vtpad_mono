import uuid

from pydantic import BaseModel

from app.src.spacesuser.model import SpacesUserRole


class GetSpaceByIdRto(BaseModel):
    id: str | uuid.UUID
    name: str
    role: SpacesUserRole | str | None = None
    sort: int | None = None
    short_name: str | None = None
    right: object
