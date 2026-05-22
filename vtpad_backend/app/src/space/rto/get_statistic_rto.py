from typing import Any

from pydantic import BaseModel


class Pads(BaseModel):
    count: int
    items_count: int


class State(BaseModel):
    item_count: int | Any
    state: str | None = None


class RunsAndBugs(BaseModel):
    count: int
    state: list[State]


class GetStatisticRto(BaseModel):
    pads: Pads
    runs: RunsAndBugs
    bugs: RunsAndBugs
