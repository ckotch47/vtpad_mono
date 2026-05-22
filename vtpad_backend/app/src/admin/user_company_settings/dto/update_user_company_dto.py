from pydantic import BaseModel

from app.src.admin.company.enum import ActiveEnum


class UpdateUserCompanyDto(BaseModel):
    status: ActiveEnum
    username: str
    mail: str
