import datetime
import uuid

from pydantic import BaseModel


class GetTestCaseListRto(BaseModel):
    id: uuid.UUID | str
    create_date: datetime.datetime
    update_date: datetime.datetime
    title: str | None = None
    link: str | None = None
    sort: int | None = None
    space_id: uuid.UUID | str
    short_name: str | None = None


class GetTestCaseListForItem(GetTestCaseListRto):
    into_item: bool | None = None
