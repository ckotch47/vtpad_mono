import uuid
from typing import Any

from pydantic import BaseModel

from app.src.testcases.rto import GetTestCaseRto


class ItemsRto(BaseModel):
    id: uuid.UUID | str
    text: str | None = None
    sort: int | None = None
    mainId: uuid.UUID | str | None = None
    pad_id: uuid.UUID | str | None = None
    subItem: Any
    testcases: list[GetTestCaseRto] | list | Any


class GetItemsRto(ItemsRto):
    id: uuid.UUID | str
    text: str | None = None
    sort: int | None = None
    mainId: uuid.UUID | str | None = None
    subItem: Any
    testcases: list[GetTestCaseRto] | list | Any


class ItemsRtoV2(BaseModel):
    id: uuid.UUID | str
    text: str | None = None
    sort: int | None = None
    description: str | None = None
    mainId: uuid.UUID | str | None = None
    pad_id: uuid.UUID | str | None = None
    subItem: Any




class GetItemsRtoV2(ItemsRtoV2):
    id: uuid.UUID | str
    text: str | None = None
    sort: int | None = None
    description: str | None = None
    mainId: uuid.UUID | str | None = None
    subItem: Any