from fastapi import HTTPException
from tortoise import Tortoise

from .model import ChecklistModel
from .dto import *
from .enum import ChecklistStatusEnum
class ChecklistService:
    model = ChecklistModel()

    async def get_checklist_list(self, space_id: str, dto: GetChecklistDto):
        conn = Tortoise.get_connection('default')

        sql = f"""
            SELECT id, create_date, update_date, title, sort, short_name, state, space_id 
            FROM checklistmodel
            WHERE space_id = $1
                AND ((lower(title) like lower('%{dto.q.split(';')[0]}%'))
                OR (lower(text) like lower('%{dto.q.split(';')[0]}%'))
                OR (lower(short_name) like lower('%{dto.q.split(';')[0]}%')))
            ORDER BY sort {dto.sort}
            LIMIT $2
            OFFSET $3
        """
        return await conn.execute_query_dict(sql, [space_id, dto.limit, dto.offset])

    async def create_checklist(self, space_id: str, dto: CreateChecklistDto):
        conn = Tortoise.get_connection('default')
        sql = """
            SELECT
                   count(checklistmodel.id),
                   (SELECT sort FROM checklistmodel WHERE space_id = $1 ORDER BY sort DESC LIMIT 1),
                   s.short_name
            FROM checklistmodel
            LEFT JOIN spacemodel s on s.id = checklistmodel.space_id
            WHERE space_id = $1
            GROUP BY s.short_name
        """
        temp = await conn.execute_query_dict(sql, [space_id, ])
        try:
            temp = temp[0]
        except:
            temp = {
                "count": 0,
                "sort": 0,
                "short_name": (await self.get_space_short_name(space_id)).get('short_name')
            }
        sort = temp.get('sort') + 1
        short_name = f"{temp.get('short_name')}-{temp.get('sort')+1}C" if temp.get('short_name') else f"{temp.get('sort')+1}C"
        return await self.model.create(
            title=dto.title,
            text=dto.text,
            sort=sort,
            short_name=short_name,
            state=dto.state if dto.state else ChecklistStatusEnum.draft,
            space_id=space_id
        )

    async def get_checklist_detail_by_id(self, checklist_id: str):
        return await self.model.filter(id=checklist_id).first()

    async def update_checklist(self, checklist_id: str, dto: CreateChecklistDto):
        checklist = await self.model.filter(id=checklist_id).get_or_none()
        if not checklist:
            raise HTTPException(status_code=404, detail=f'not found')

        tmp = {
            "title": dto.title if dto.title else checklist.title,
            "text":  dto.text if dto.text else checklist.text,
            "state": dto.state if dto.state else checklist.state
        }
        await checklist.update_from_dict(tmp)
        await checklist.save()
        return checklist


    async def delete_checklist_by_id(self, checklist_id: str):
        return await self.model.filter(id=checklist_id).delete()

    async def get_space_short_name(self, space_id: str):
        conn = Tortoise.get_connection('default')
        sql = """
            SELECT short_name from spacemodel WHERE id = $1
        """
        return (await conn.execute_query_dict(sql, [space_id, ]))[0]

    async def get_checklist_by_short_name(self, short_name: str, user: dict):
        conn = Tortoise.get_connection('default')
        sql = """
            SELECT checklistmodel.id FROM checklistmodel
            left outer join spacemodel s on s.id = checklistmodel.space_id
            left join companymodel c on c.id = s.company_id
            WHERE checklistmodel.short_name = $1
            AND c.id = $2;
        """
        try:
            tmp = await conn.execute_query_dict(sql, [short_name, user.get('company')])
            if len(tmp) == 1:
                return tmp[0]
            else:
                raise HTTPException(status_code=404, detail=f'not fount')
        except:
            raise HTTPException(status_code=404, detail=f'not fount')


    async def check_user_into_space_by_checklist_id(self, user: dict, checklist_id: str):
        conn = Tortoise.get_connection('default')
        sql = """
            SELECT checklistmodel.id FROM checklistmodel
            left outer join spacemodel s on s.id = checklistmodel.space_id
            left join companymodel c on s.company_id = c.id
            WHERE checklistmodel.id = $1
            AND c.id = $2
        """
        try:
            tmp = await conn.execute_query_dict(sql, [checklist_id, user.get('company')])
            if tmp[0]:
                return True
            else:
                raise HTTPException(status_code=404, detail="not found")
        except:
            raise HTTPException(status_code=404, detail="not found")
