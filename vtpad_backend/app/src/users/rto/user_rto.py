import uuid

from pydantic import BaseModel


class AvatarRto(BaseModel):
    id: str | uuid.UUID | None = None
    filepath: str | None = None


class UserRto(BaseModel):
    id: str | uuid.UUID
    username: str | None = None
    mail: str
    avatar_id: str | uuid.UUID | None = None
    avatar: AvatarRto
