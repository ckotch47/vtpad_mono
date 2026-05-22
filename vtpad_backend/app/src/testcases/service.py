import tortoise
from fastapi import HTTPException

from .dto import *
from .model import TestCasesModel
from ..bug.service import parse_external_link
from ..testcases_paditem.model import TestCasePadItemModel
from ..testcases_image.service import TestCaseImageService
from tortoise import Tortoise
import uuid


class TestCasesService:
    def __init__(self):
        self.test_case_model = TestCasesModel()
        self.test_case_pad_item_model = TestCasePadItemModel()
        self.test_cse_image_service = TestCaseImageService()

    async def get_last_sort(self, space_id: str):
        last_sort = await self.test_case_model.filter(space_id=space_id).order_by('-sort').first()
        try:
            sort = ((last_sort.sort / 10) + 1) * 10
        except Exception as e:
            sort = 10
        return int(sort)

    async def get_short_name(self, space_id: str):
        conn = Tortoise.get_connection('default')
        sql = "SELECT short_name FROM spacemodel WHERE id = $1"
        temp = (await conn.execute_query_dict(sql, [space_id]))[0]['short_name']
        return temp if temp else ''

    async def create_test_case(self, dto: CreateTestCaseDto):
        sort = await self.get_last_sort(dto.space_id)
        count = await self.test_case_model.filter(space_id=uuid.UUID(dto.space_id)).count()
        short_name = await self.get_short_name(dto.space_id)
        return await self.test_case_model.create(
            title=dto.title,
            text=dto.text,
            steps=dto.steps,
            sort=sort,
            link=dto.link,
            expected_results=dto.expected_results,
            space_id=uuid.UUID(dto.space_id),
            short_name=f'{short_name + "-" if short_name else ""}{count}T'
        )

    async def get_filter_for_space(self, space_id):
        conn = Tortoise.get_connection('default')
        sql = "SELECT DISTINCT link FROM testcasesmodel \
                WHERE link IS NOT NULL \
                AND space_id = $1"
        res = []
        for i in await conn.execute_query_dict(sql, [space_id]):
            res.append(parse_external_link(i.get('link')))
        return res

    async def get_test_case_list_by_space_id(self, space_id: str, dto: GetTestcaseDto):
        conn = Tortoise.get_connection('default')
        order_direction = dto.sort.upper() if dto.sort and dto.sort.upper() in ('ASC', 'DESC') else 'DESC'
        sql = "SELECT id, create_date, update_date, title, sort, space_id, short_name FROM testcasesmodel \
                        WHERE space_id = $1 \
                        AND (lower(title) like lower($2) " \
              "OR lower(link) like lower($2) " \
              "OR lower(text) like lower($2) " \
              "OR lower(short_name) like lower($2)) \
                        ORDER BY sort " + order_direction + " \
              " \
              "LIMIT $3 " \
              "OFFSET $4"
        return await conn.execute_query_dict(sql, [space_id, f"%{dto.q}%", dto.limit, dto.offset])

    async def get_test_case_by_paditem_id(self, item_id: str):
        conn = Tortoise.get_connection('default')
        sql = "SELECT t.id, t.create_date, t.update_date, " \
              "t.title, t.sort, t.space_id, t.short_name FROM testcasepaditemmodel " \
              "LEFT JOIN testcasesmodel t on testcasepaditemmodel.testcases_id = t.id " \
              "WHERE testcasepaditemmodel.pad_item_id = $1"
        return await conn.execute_query_dict(sql, [item_id])

    async def update_test_case(self, dto: UpdateTestCaseDto, case_id: str):
        case = await self.test_case_model.filter(id=case_id).get()
        for i in dto:
            if i[0]:
                case.__setattr__(i[0], i[1])

        await case.save()
        if dto.pad_item_id:
            await self.test_case_pad_item_model.create(
                pad_item_id=dto.pad_item_id,
                testcases_id=case.id
            )
        temp = {}
        temp.update(case)
        temp.update({"pad_item_id": await self.test_case_pad_item_model.filter(testcases_id=case.id)})
        return temp

    async def delete_test_case(self, case_id: str):
        return bool(await self.test_case_model.filter(id=case_id).delete())

    async def get_test_cases_detail(self, case_id: str):
        case = await self.test_case_model.filter(id=case_id).get()
        tmp = {}
        tmp.update(case)
        tmp.update({"pad_item_id": await self.test_case_pad_item_model.filter(testcases_id=case.id)})
        return tmp

    async def get_test_cases_for_item(self, item_id: str, dto: GetTestcaseItemDto):
        if not dto.with_all:
            conn = Tortoise.get_connection('default')
            order_direction = dto.sort.upper() if dto.sort and dto.sort.upper() in ('ASC', 'DESC') else ''
            order_clause = f"ORDER BY t2.sort {order_direction}" if order_direction else ""
            sql = "SELECT t2.id, t2.create_date, t2.update_date, t2.title, t2.sort, t2.space_id, t2.short_name, t2.link, t2.space_id from itemsmodel " \
                  "LEFT JOIN testcasepaditemmodel t on itemsmodel.id = t.pad_item_id " \
                  "LEFT JOIN testcasesmodel t2 on t.testcases_id = t2.id " \
                  "WHERE itemsmodel.id = $1 " + order_clause
            testcase_by_item_select = await conn.execute_query_dict(sql, [item_id])
            if testcase_by_item_select[0]['id'] is None:
                return []
            return testcase_by_item_select

        else:
            conn = Tortoise.get_connection('default')
            sql = "SELECT array_agg(t2.id) as id, t2.space_id from itemsmodel " \
                  "LEFT JOIN testcasepaditemmodel t on itemsmodel.id = t.pad_item_id " \
                  "LEFT JOIN testcasesmodel t2 on t.testcases_id = t2.id " \
                  "WHERE itemsmodel.id = $1 " \
                  "GROUP BY t2.space_id"

            testcase_by_item_select = await conn.execute_query_dict(sql, [item_id])

            select_item_id = testcase_by_item_select[0]['id']
            if select_item_id[0] is None:
                testcase_by_item_select = await conn.execute_query_dict(
                    "SELECT p.spaces_id FROM itemsmodel LEFT JOIN padmodel p on itemsmodel.pad_id = p.id WHERE itemsmodel.id = $1",
                    [item_id])
                space_id = testcase_by_item_select[0]['spaces_id']
            else:
                space_id = testcase_by_item_select[0]['space_id']

            testcase_space = await self.get_test_case_list_by_space_id(space_id, GetTestcaseDto(q=dto.q, sort=dto.sort))

            temp = []
            for i in testcase_space:
                if i.get('id'):
                    temp.append({
                        # "expected_results": i.get('expected_results'),
                        "id": i.get('id'),
                        "create_date": i.get('create_date'),
                        "update_date": i.get('update_date'),
                        "title": i.get('title'),
                        "sort": i.get('sort'),
                        "space_id": i.get('space_id'),
                        "short_name": i.get('short_name'),
                        "into_item": True if i.get('id') in select_item_id else False
                    })

            return temp

    async def delete_case_from_paditem(self, case_id, paditem_id):
        return bool(await self.test_case_pad_item_model.filter(pad_item_id=paditem_id, testcases_id=case_id).delete())

    async def add_image(self, case_id: str, dto: AddImageTestcaseDto):
        return await self.test_cse_image_service.add_image_to_case(case_id, dto.image_id)

    async def delete_image(self, case_id: str, image_id: str):
        return await self.test_cse_image_service.delete_image_from_case(case_id, image_id)

    async def get_case_by_short_name(self, short_name: str, user: dict):
        conn = Tortoise.get_connection('default')
        sql = """
            SELECT testcasesmodel.id FROM testcasesmodel
            LEFT JOIN spacemodel s on s.id = testcasesmodel.space_id
            LEFT JOIN companymodel c on s.company_id = c.id
            WHERE testcasesmodel.short_name = $1
            AND c.id = $2
        """

        try:
            tmp = await conn.execute_query_dict(sql, [short_name, user.get('company')])
            if len(tmp) == 1:
                return tmp[0]
            else:
                raise HTTPException(status_code=404, detail='not fount')
        except Exception:
            raise HTTPException(status_code=404, detail='not fount')