from .add_company_dto import AddCompanyDto
from ..enum import ActiveEnum


class UpdateCompanyDto(AddCompanyDto):
    status: ActiveEnum
