import uuid

from pydantic import BaseModel

from app.src.admin.company.enum import ActiveEnum
from app.src.users.rto import UserRto


class GetCompanyUserRto(BaseModel):
    id: uuid.UUID | str
    status: ActiveEnum
    company_id: uuid.UUID | str
    role: str
    user: UserRto
