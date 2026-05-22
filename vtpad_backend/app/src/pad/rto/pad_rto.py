import uuid

from pydantic import BaseModel


class PadRto(BaseModel):
    id: uuid.UUID | str
    name: str | None = None
    spaces_id: uuid.UUID | str
    sort: int
    folder_id: uuid.UUID | str | None = None
