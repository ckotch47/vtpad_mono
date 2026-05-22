import uuid

from pydantic import BaseModel

from app.src.runitems.dto import State
from app.src.testcases.rto import GetTestCaseRto


class RunItemsTestcases(BaseModel):
    id: uuid.UUID | str
    state: State | None = None
    run_item_id: uuid.UUID | str
    testcases_id: uuid.UUID | str
    testcase: list[GetTestCaseRto]


class Item(BaseModel):
    id: uuid.UUID | str
    itemId: uuid.UUID | str
    text: str | None = None
    sort: int
    state: State | None = None
    mainId: uuid.UUID | str | None = None
    subItem: list
    runItemsTestcases: list


class Items(Item):
    subItem: list[Item]
    runItemsTestcases: list[RunItemsTestcases]


class GetItemsForRunRto(BaseModel):
    item: list[Items]
    allCount: int
    passed: int
    failed: int
