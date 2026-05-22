import datetime
import uuid

from pydantic import BaseModel


class GetTagRto(BaseModel):
    id: str | uuid.UUID
    title: str
    color: str
    create_date: datetime.datetime | None = None
    space_id: str | uuid.UUID | None = None
