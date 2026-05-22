import datetime
import uuid

from pydantic import BaseModel
from ..enum import ChecklistStatusEnum


class ChecklistRto(BaseModel):
    id: uuid.UUID | str
    create_date: datetime.datetime | str
    update_date: datetime.datetime | str
    short_name: str
    title: str | None = None
    text: str | None = None
    sort: int
    state: ChecklistStatusEnum
    space_id: uuid.UUID | str
