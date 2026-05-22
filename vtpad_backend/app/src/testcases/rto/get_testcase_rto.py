import datetime
import uuid

from pydantic import BaseModel


class GetTestCaseRto(BaseModel):
    id: uuid.UUID | str
    create_date: datetime.datetime
    update_date: datetime.datetime
    title: str
    text: str | None = None
    steps: str | None = None
    expected_results: str | None = None

    sort: int | None = None

    short_name: str | None = None
    link: str | None = None

    space_id: uuid.UUID | str
