import datetime
import uuid
from typing import Any

from pydantic import BaseModel


class ItemsCount(BaseModel):
    all: int
    failed: int
    passed: int


class Runs(BaseModel):
    id: str | uuid.UUID
    name: str
    date: datetime.datetime
    items_count: ItemsCount


class Pad(BaseModel):
    pad_id: str | uuid.UUID
    pad_name: str | Any
    runs: list[Runs]


class GetAllRunsForSpaceRto(BaseModel):
    space_name: str | Any
    space_id: str | uuid.UUID
    pad: list[Pad] | Any
