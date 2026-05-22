from tortoise import Tortoise

from .model import CompanyModel
from .dto import *


class CompanyService:
    model = CompanyModel

    @staticmethod
    async def get_company_list(dto: GetCompanyListDto):
        conn = Tortoise.get_connection('default')
        sql = "SELECT * FROM companymodel WHERE name LIKE $1 OFFSET $2 LIMIT $3"
        return await conn.execute_query_dict(sql, [f"%{dto.q}%", dto.limit, dto.offset])

    async def create_company(self, dto: AddCompanyDto):
        return await self.model.create(
            name=dto.name,
            max_person=dto.max_person
        )

    async def update_company(self, dto: UpdateCompanyDto, company_id: str):
        await self.model.filter(id=company_id).update(name=dto.name, max_person=dto.max_person)
        return await self.model.filter(id=company_id).get()

    async def get_space_for_company(self, user: dict):
        conn = Tortoise.get_connection('default')
        sql = """
            SELECT spacemodel.* FROM spacemodel
            LEFT JOIN usercompanysettingsmodel u on u.user_id = $1
            WHERE spacemodel.company_id = u.company_id
            AND u.status = 'active' 
        """
        return await conn.execute_query_dict(sql, [user.get('id')])