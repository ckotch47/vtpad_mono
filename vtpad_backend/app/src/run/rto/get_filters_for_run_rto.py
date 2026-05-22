import uuid

from pydantic import BaseModel


class GetFilterForRunRto(BaseModel):
    id: uuid.UUID | str
    name: str
