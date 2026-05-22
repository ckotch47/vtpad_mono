import datetime
import uuid

from pydantic import BaseModel

from app.src.admin.company.enum import ActiveEnum


class CompanyRto(BaseModel):
    id: uuid.UUID | str
    create_date: datetime.datetime | str
    name: str
    status: ActiveEnum
    max_person: int
