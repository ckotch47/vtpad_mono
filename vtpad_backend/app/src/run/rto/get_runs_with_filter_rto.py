import datetime
import uuid
from typing import Any

from pydantic import BaseModel


class ItemsCount(BaseModel):
    passed: int
    fail: int
    all: int


class GetRunsWithFilterRto(BaseModel):
    id: uuid.UUID | str | Any
    date: datetime.datetime | str | Any
    name: str | Any
    items_count: ItemsCount | Any
