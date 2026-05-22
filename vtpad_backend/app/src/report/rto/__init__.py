import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

class BaseReportRto(BaseModel):
    id: uuid.UUID | str
    create_at: datetime | str
    update_at: datetime | str
    name: str
    duration: str


class TestRto(BaseReportRto):
    space_id: uuid.UUID | str


class Statistic(BaseModel):
    passed: int
    skipped: int
    failed: int
    unknown: int


class GetTestListRto(TestRto):
    pass


class GetTestDetailRto(TestRto):
    statistic: Statistic | Any


class SuiteRto(BaseReportRto):
    test_id: uuid.UUID | str
    statistic: Statistic


class TestCaseRto(BaseReportRto):
    status: str
    message: str | None
    suits_id: uuid.UUID | str