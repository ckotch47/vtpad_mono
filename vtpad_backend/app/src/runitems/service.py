from typing import Union

from tortoise import Tortoise

from .model import RunItemsModel
from .dto import *
from ..testcases_runitem.model import TestCaseRunItemModel
import json

def get_sub_item(main_id: str, arr: list):
    res = []
    indexs = []
    for index, item in enumerate(arr):
        if item['mainId'] == main_id:
            arr[index]['subItem'] = get_sub_item(item['itemId'], arr)
            indexs.append(index)

    for i in indexs:
        res.append(arr[i])
    return res


def add_sub_items_properety(arr):
    res = []
    main_arr = []
    for index, i in enumerate(arr):
        i['run_items_case'] = json.loads(i['run_items_case'])

        i['cases'] = json.loads(i['cases'])

        testcases = []
        try:
            for j in i['run_items_case']:
                j['testcase'] = list(filter(lambda x: (x['id'] == j['testcases_id']), i['cases']))[0]
                testcases.append(j)
            testcases.sort(key=lambda x: x['testcase']['sort'], reverse=False)
        except Exception:
            pass
        res.append({
            'id': i['id'],
            'itemId': i['itemId'],
            'text': i['text'],
            'sort': i['sort'],
            'state': i['state'],
            'mainId': i['mainId'],
            'subItem': [],
            'runItemsTestcases': testcases
        })
        if not i['mainId']:
            main_arr.append({
                'id': i['id'],
                'itemId': i['itemId'],
                'text': i['text'],
                'sort': i['sort'],
                'state': i['state'],
                'mainId': i['mainId'],
                'subItem': [],
                'runItemsTestcases': testcases
            })

    for i in main_arr:
        if not i['mainId']:
            i['subItem'] = get_sub_item(i['itemId'], res)

    return main_arr


class RunItemsService:
    @staticmethod
    async def create_run_item(run_id: str):
        conn = Tortoise.get_connection("default")
        run = await conn.execute_query_dict("SELECT * FROM runmodel WHERE id = $1", [run_id])
        pad = run[0].get('pads_id')
        sql = "SELECT itemsmodel.*, array_agg(t.testcases_id) as case_id FROM itemsmodel " \
              "LEFT JOIN testcasepaditemmodel t on itemsmodel.id = t.pad_item_id " \
              "WHERE pad_id = $1 " \
              "GROUP BY itemsmodel.id "

        items = await conn.execute_query_dict(sql, [pad])
        temp = []

        for item in items:
            temp = await RunItemsModel.create(
                itemId=item.get('id'),
                run_id=run_id
            )
            try:
                for case_id in item.get('case_id'):
                    await TestCaseRunItemModel.create(
                        run_item_id=temp.id,
                        testcases_id=case_id
                    )
            except Exception:
                pass

        return temp

    @staticmethod
    async def get_item_for_run(run_id: str):
        conn = Tortoise.get_connection("default")
        sql = "SELECT itemsmodel.*, " \
              "runitemsmodel.*, " \
              "array_to_json(array_agg(t.*)) as run_items_case, " \
              "array_to_json(array_agg(json_build_object('id',t2.id, 'create_data',t2.create_date, 'update_date',t2.update_date, 'title',t2.title, 'sort',t2.sort, 'space_id',t2.space_id, 'short_name', t2.short_name, 'link',t2.link))) as cases FROM itemsmodel " \
            "LEFT JOIN runitemsmodel ON itemsmodel.id = runitemsmodel.\"itemId\" " \
            "LEFT JOIN testcaserunitemmodel t on t.run_item_id = runitemsmodel.id " \
            "LEFT JOIN testcasesmodel t2 on t.testcases_id = t2.id " \
            "WHERE  runitemsmodel.run_id = $1 " \
            "GROUP BY itemsmodel.id, itemsmodel.sort, runitemsmodel.id " \
            "ORDER BY itemsmodel.sort ASC "

        main_items = await conn.execute_query_dict(sql, [run_id])

        return {
            "items": add_sub_items_properety(main_items),
            "allCount": len(list(filter(lambda x: (x['id']), main_items))),
            "passed": len(list(filter(lambda x: (x['state'] == 'pass'), main_items))),
            "failed": len(list(filter(lambda x: (x['state'] == 'fail'), main_items))),
        }

    @staticmethod
    async def update_run_item(item_id: str, state: State):
        return bool(await RunItemsModel.filter(id=item_id).update(state=state))

    @staticmethod
    async def get_count_state_item(run_id: str, state: Union[str, None]):
        if type(state) is str:
            return await RunItemsModel.filter(run_id=run_id, state=state).count()
        else:
            return await RunItemsModel.filter(run_id=run_id).count()
