import datetime
import uuid
from typing import Any

from pydantic import BaseModel


class RunRto(BaseModel):
    id: uuid.UUID | str
    name: str
    date: datetime.datetime | None = None
    pads_id: uuid.UUID | str