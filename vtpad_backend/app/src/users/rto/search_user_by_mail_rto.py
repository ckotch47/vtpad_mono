import uuid

from pydantic import BaseModel


class SearchUserByMail(BaseModel):
    id: str | uuid.UUID
    username: str | None = None
    mail: str
    avatar_id: str | uuid.UUID | None = None
