import json
import uuid

from tortoise import Tortoise

from .model import ItemsModel
from .dto import *
from fastapi import HTTPException


def get_sub_item(main_id: str, arr: list):
    res = []
    indexs = []
    for index, item in enumerate(arr):
        if item['mainId'] == main_id:
            arr[index]['subItem'] = get_sub_item(item['id'], arr)
            indexs.append(index)

    for i in indexs:
        res.append(arr[i])
    return res


def collect_id_for_delete(main_id: str, arr: list):
    res = []
    for i in arr:
        res.append({
            'id': str(i.id),
            'mainId': str(i.mainId),
            'subItem': []
        })
    res = get_sub_item(main_id, res)

    res = get_id_for_delete(res)

    sql = f"('{main_id}'"
    for i in res:
        sql += f", '{i}'"

    sql += ')'
    return sql


def get_id_for_delete(arr: list):
    res = []
    for i in arr:
        res.append(i['id'])
        if i['subItem']:
            for j in get_id_for_delete(i['subItem']):
                res.append(j)
    return res


def add_sub_items_properety(arr):
    res = []
    main_arr = []
    for index, i in enumerate(arr):

        res.append({
            'id': i.get('id'),
            'text': i.get('text'),
            'sort': i.get('sort'),
            'mainId': i.get('mainId'),
            'subItem': [],
            'testcases': i.get('testcases') if i.get('testcases')[0]['id'] else "[]"
        })
        if not i.get('mainId'):
            main_arr.append({
                'id': i.get('id'),
                'text': i.get('text'),
                'sort': i.get('sort'),
                'mainId': i.get('mainId'),
                'subItem': [],
                'testcases': i.get('testcases') if i.get('testcases')[0]['id'] else "[]"
            })

    for i in main_arr:
        if not i['mainId']:
            i['subItem'] = get_sub_item(i['id'], res)

    return main_arr

def add_sub_items_properetyV2(arr):
    res = []
    main_arr = []
    for index, i in enumerate(arr):

        res.append({
            'id': i.get('id'),
            'text': i.get('text'),
            'sort': i.get('sort'),
            'description': i.get('description'),
            'mainId': i.get('mainId'),
            'subItem': [],
            'pad_id': i.get('pad_id')

        })
        if not i.get('mainId'):
            main_arr.append({
                'id': i.get('id'),
                'text': i.get('text'),
                'sort': i.get('sort'),
                'description': i.get('description'),
                'mainId': i.get('mainId'),
                'subItem': [],
                'pad_id': i.get('pad_id')
            })

    for i in main_arr:
        if not i['mainId']:
            i['subItem'] = get_sub_item(i['id'], res)

    return main_arr

class ItemsService:
    @staticmethod
    async def create_item(pad_id: str, item: CreateItemDto):
        main_id = item.mainId
        try:
            last_sort = await ItemsModel.filter(pad_id=pad_id, mainId=main_id).order_by('-sort').first()
            try:
                sort = ((last_sort.sort / 10) + 1) * 10
            except:
                sort = 10

            temp = await ItemsModel.create(
                text=item.text,
                sort=int(sort),
                pad_id=pad_id,
                mainId=main_id
            )
            return {
                'id': temp.id,
                'text': temp.text,
                'sort': temp.sort,
                'mainId': temp.mainId,
                'pad_id': pad_id,
                'subItem': [],
                'testcases': []
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')

    @staticmethod
    async def get_items(pad_id: str):
        try:
            conn = Tortoise.get_connection('default')
            sql = f"SELECT itemsmodel.*, array_to_json(" \
                  f"array_agg(" \
                  f"json_build_object('id',t2.id, 'create_data',t2.create_date, 'update_date',t2.update_date, 'title',t2.title, 'sort',t2.sort, 'space_id',t2.space_id, 'short_name', t2.short_name, 'link',t2.link) " \
                  f"ORDER BY t2.sort)) " \
                  f"as testcases FROM itemsmodel " \
                  f"LEFT JOIN testcasepaditemmodel t on itemsmodel.id = t.pad_item_id " \
                  f"LEFT JOIN testcasesmodel t2 on t.testcases_id = t2.id " \
                  f"WHERE itemsmodel.pad_id = '{pad_id}' " \
                  f"GROUP BY itemsmodel.id, itemsmodel.sort " \
                  f"ORDER BY itemsmodel.sort "
            temp = await conn.execute_query_dict(sql)
            for i in temp:
                i['testcases'] = json.loads(i.get('testcases') if i.get('testcases') else "[]")
            # temp = await ItemsModel.filter(pad_id=pad_id).order_by('sort')
            return add_sub_items_properety(temp)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')


    @staticmethod
    async def update_item(item_id: str, item: UpdateItemDto):
        try:
            return bool(await ItemsModel.filter(id=item_id).update(text=item.text))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')

    @staticmethod
    async def delete_item(item_id: str):
        try:
            all_item = await ItemsModel.filter(pad_id=str((await ItemsModel.filter(id=item_id).get()).pad_id))
            sql = f"DELETE from itemsmodel WHERE id in { collect_id_for_delete(item_id, all_item)}"

            await ItemsModel.raw(sql)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')

    @staticmethod
    async def update_path_item(item_id: str, dto: UpdateSortItemDto):
        temp = None
        if dto.sortBeforeId:
            temp = await ItemsModel.filter(id=dto.sortBeforeId).get()
            temp1 = await ItemsModel.filter(id=item_id).get()  # .update(sort=(temp.sort - 1))
            await ItemsModel.filter(id=dto.sortBeforeId).update(sort=temp1.sort)
            await ItemsModel.filter(id=item_id).update(sort=temp.sort)
        if dto.sortAfterId:
            temp = await ItemsModel.filter(id=dto.sortAfterId).get()
            temp1 = await ItemsModel.filter(id=item_id).get()
            await ItemsModel.filter(id=dto.sortAfterId).update(sort=temp1.sort)
            await ItemsModel.filter(id=item_id).update(sort=temp.sort)

        try:
            return await ItemsService.get_items(str(temp.pad_id))
        except:
            return True

class ItemsServiceV2:
    conn = None

    def __call__(self, *args, **kwargs):
        if not self.conn:
            self.conn = Tortoise.get_connection('default')

    def get_conn(self):
        if not self.conn:
            self.conn = Tortoise.get_connection('default')
        return self.conn
    async def get_items(self, pad_id: str):
        try:
            sql = """
                select itemsmodel.*
                from itemsmodel
                where itemsmodel.pad_id = $1
                order by itemsmodel.sort;
            """
            temp = await self.get_conn().execute_query_dict(sql, [pad_id])

            return add_sub_items_properetyV2(temp)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')

    async def get_checklist(self, item_id: uuid.UUID):
        sql = """
        select c.*
        from itemschecklisttestcasemodel
        left join checklistmodel c on c.id = itemschecklisttestcasemodel.checklist_id
        where item_id = $1
        and checklist_id is not null;
        """
        return await self.get_conn().execute_query_dict(sql, [item_id])

    async def get_testcase(self, item_id: uuid.UUID):
        sql = """
        select t.*
        from itemschecklisttestcasemodel
        left join testcasesmodel t on t.id = itemschecklisttestcasemodel.testcase_id
        where item_id = $1
        and itemschecklisttestcasemodel.testcase_id is not null;
        """
        return await self.get_conn().execute_query_dict(sql, [item_id])

    async def add_checklist(self, item_id: uuid.UUID, checklist_id: uuid.UUID):
        sql = """
            insert into itemschecklisttestcasemodel(item_id, checklist_id) values ($1, $2);
        """
        try:
            await self.get_conn().execute_query(sql, [item_id, checklist_id])
            return True
        except:
            return False

    async def add_testcase(self, item_id: uuid.UUID, testcase_id: uuid.UUID):
        sql = """
            insert into itemschecklisttestcasemodel(item_id, testcase_id) values ($1, $2);
        """
        try:
            await self.get_conn().execute_query(sql, [item_id, testcase_id])
            return True
        except:
            return False

    async def remove_checklist(self, item_id: uuid.UUID, checklist_id: uuid.UUID):
        sql = """
            delete
            from itemschecklisttestcasemodel
            where item_id = $1
            and checklist_id = $2;
        """
        try:
            await self.get_conn().execute_query(sql, [item_id, checklist_id])
            return True
        except:
            return False

    async def remove_testcase(self, item_id: uuid.UUID, testcase_id: uuid.UUID):
        sql = """
            delete
            from itemschecklisttestcasemodel
            where item_id = $1
            and testcase_id = $2;
        """
        try:
            await self.get_conn().execute_query(sql, [item_id, testcase_id])
            return True
        except:
            return False
