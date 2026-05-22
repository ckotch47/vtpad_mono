import uuid

from pydantic import BaseModel


class GetByShortName(BaseModel):
    id: uuid.UUID | str