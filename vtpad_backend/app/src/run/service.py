import json
from asyncio import sleep
from datetime import datetime

from tortoise import Tortoise

from .model import RunModel
from ..pad.service import PadService
from ..runitems import RunItemsService
from .dto import *


class RunService:
    @staticmethod
    async def create_run(pad_id: str, run: CreateRunDto):
        temp = await RunModel.create(
            name=run.name,
            date=datetime.now(),
            pads_id=pad_id
        )
        await RunItemsService.create_run_item(temp.id)
        return temp

    @staticmethod
    async def get_items_for_run(run_id: str):
        temp = await RunItemsService.get_item_for_run(run_id)
        return temp

    @staticmethod
    async def get_all_run(pad_id: str):
        return await RunModel.filter(pads_id=pad_id).order_by('-date')

    @staticmethod
    async def get_filter_for_run(space_id: str):
        conn = Tortoise.get_connection('default')
        sql = f"SELECT DISTINCT p.name, p.id FROM runmodel \
                LEFT JOIN padmodel p on runmodel.pads_id = p.id \
                WHERE spaces_id = '{space_id}'"
        return await conn.execute_query_dict(sql)

    @staticmethod
    async def get_runs_with_filter(dto: GetRunsDto):
        runs = []
        run = await RunModel.filter(pads_id=dto.pad_id).limit(dto.limit).offset(dto.skip).order_by('-date')
        for j in run:
            runs.append({
                "name": j.name,
                "id": j.id,
                "date": j.date,
                "items_count": {
                    "pass": await RunItemsService.get_count_state_item(j.id, 'pass'),
                    "fail": await RunItemsService.get_count_state_item(j.id, 'fail'),
                    "all": await RunItemsService.get_count_state_item(j.id, None)
                }
            })
        return runs

    @staticmethod
    async def delete_run(run_id: str):
        return bool(await RunModel.filter(id=run_id).delete())

    @staticmethod
    async def get_run(run_id: str):
        return await RunModel.filter(id=run_id).first()

    @staticmethod
    async def update_run(run_id: str, name: str):
        return bool(await RunModel.filter(id=run_id).update(name=name))

    #V2
    @staticmethod
    async def get_all_runs_spaces(space_id):
        conn = Tortoise.get_connection('default')

        pad: dict = await PadService.get_all_pad(space_id)

        res = []

        for i in pad:
            runs = []

            run = await RunService.get_all_run(i.id)
            for j in run:
                runs.append({
                    "name": j.name,
                    "id": j.id,
                    "date": j.date,
                    "items_count": {
                        "pass": await RunItemsService.get_count_state_item(j.id, 'pass'),
                        "fail": await RunItemsService.get_count_state_item(j.id, 'fail'),
                        "all": await RunItemsService.get_count_state_item(j.id, None)
                    }
                })
            res.append({
                "pad_id": i.id,
                "pad_name": i.name,
                "run": runs
            })

        return {
            "space_id": space_id,
            "space_name": space_id,
            "pad": res
        }

    @staticmethod
    async def get_last_run(space_id: str):
        conn = Tortoise.get_connection('default')
        sql = f"SELECT p.*, json_agg(runmodel.*) as runs FROM runmodel \
                LEFT JOIN padmodel p on p.id = runmodel.pads_id \
                WHERE p.spaces_id = $1 \
                GROUP BY p.id, runmodel.date \
                ORDER BY runmodel.date DESC\
                LIMIT 3"
        tmp = await conn.execute_query_dict(sql, [space_id, ])
        res = []
        for i in tmp:
            runs = []
            temp = json.loads(i['runs'])
            for j in temp:
                runs.append({
                    "name": j['name'],
                    "id": j['id'],
                    "date": j['date'],
                    "items_count": {
                        "pass": await RunItemsService.get_count_state_item(j['id'], 'pass'),
                        "fail": await RunItemsService.get_count_state_item(j['id'], 'fail'),
                        "all": await RunItemsService.get_count_state_item(j['id'], None)
                    }
                })
            res.append({
                "pad_id": i['id'],
                "pad_name": i['name'],
                "run": runs
            })
        return {
            "space_id": space_id,
            "space_name": space_id,
            "pad": res
        }

    @staticmethod
    async def re_run_run_by_id(run_id: str):
        sql = f"UPDATE runitemsmodel \
                SET state = null \
                WHERE run_id = $1"
        conn = Tortoise.get_connection('default')
        return bool(await conn.execute_query_dict(sql, [run_id, ]))