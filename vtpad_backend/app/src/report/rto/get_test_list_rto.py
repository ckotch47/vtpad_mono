import uuid
from datetime import datetime

from pydantic import BaseModel


class TestRto(BaseModel):
    id: uuid.UUID | str
    create_at: datetime | str
    update_at: datetime | str
    name: str
    duration: str
    space_id: uuid.UUID | str


class GetTestListRto(TestRto):
    pass
