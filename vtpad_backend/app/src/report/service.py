import json
import uuid

import requests
from tortoise import Tortoise

from app.src import common


class ReportService:
    http_timeout = 6

    def __init__(self):
        self.req = requests
        self.config = common.EnvConfig()
        self.header = {
            "api-token": self.config.report_api_hash
        }
        self.url = self.config.report_portal_url

    async def get_test_list(self, space_id: str):
        try:
            temp = self.req.get(
                url=f"{self.url}/test/{space_id}/list",
                timeout=self.http_timeout,
                headers=self.header
            )
            if temp.status_code == 200:
                return temp.json()
            return []
        except:
            return []

    async def get_test_detail(self, test_id: str):
        try:
            temp = self.req.get(
                url=f"{self.url}/test/{test_id}/detail",
                timeout=self.http_timeout,
                headers=self.header
            )
            if temp.status_code == 200:
                return temp.json()
            return []
        except:
            return []


class ReportServiceV2:
    async def get_test_list(self, space_id: uuid.UUID):
        conn = Tortoise.get_connection('report')
        sql = "SELECT id, create_at, update_at, name, duration, space_id FROM testmodel \
                WHERE space_id = $1 \
                LIMIT 100 OFFSET 0"
        return await conn.execute_query_dict(sql, [space_id, ])

    async def get_test_detail(self, space_id: str, test_id: str):
        conn = Tortoise.get_connection('report')
        sql = "SELECT testmodel.*, \
                       (jsonb_build_object( \
                           'passed', (SELECT count(testcasemodel.id) FROM testcasemodel WHERE testcasemodel.suits_id IN (SELECT id FROM suitsmodel WHERE test_id = $1 AND status = 'PASSED')), \
                           'skipped', (SELECT count(testcasemodel.id) FROM testcasemodel WHERE testcasemodel.suits_id IN (SELECT id FROM suitsmodel WHERE test_id = $1 AND status = 'SKIPPED')), \
                           'failed', (SELECT count(testcasemodel.id) FROM testcasemodel WHERE testcasemodel.suits_id IN (SELECT id FROM suitsmodel WHERE test_id = $1 AND status = 'FAILED')), \
                           'unknown', (SELECT count(testcasemodel.id) FROM testcasemodel WHERE testcasemodel.suits_id IN (SELECT id FROM suitsmodel WHERE test_id = $1 AND status NOT IN ('PASSED', 'SKIPPED', 'FAILED'))) \
                           )) as statistic \
                FROM testmodel \
                WHERE testmodel.id = $1 \
                AND space_id = $2"
        tmp = await conn.execute_query_dict(sql, [test_id, space_id, ])
        if len(tmp) < 1:
            return {}
        tmp = tmp[0]
        tmp["statistic"] = json.loads(tmp['statistic'])
        return tmp

    async def get_suite_list(self, test_id: str):
        conn = Tortoise.get_connection('report')
        sql = "SELECT suitsmodel.*, \
                   (json_build_object( \
                       'passed', (SELECT count(testcasemodel.id) FROM testcasemodel WHERE testcasemodel.suits_id = suitsmodel.id AND status = 'PASSED'), \
                       'skipped', (SELECT count(testcasemodel.id) FROM testcasemodel WHERE testcasemodel.suits_id = suitsmodel.id AND status = 'SKIPPED'), \
                       'failed', (SELECT count(testcasemodel.id) FROM testcasemodel WHERE testcasemodel.suits_id = suitsmodel.id AND status = 'FAILED'), \
                       'unknown', (SELECT count(testcasemodel.id) FROM testcasemodel WHERE testcasemodel.suits_id = suitsmodel.id AND status NOT IN ('PASSED', 'SKIPPED', 'FAILED')) \
                       )) as statistic \
            FROM suitsmodel \
            WHERE suitsmodel.test_id = $1 \
            LIMIT 100 OFFSET 0"
        tmp = await conn.execute_query_dict(sql, [test_id, ])
        for i in tmp:
            i["statistic"] = json.loads(i['statistic'])
        return tmp

    async def get_suite_detail(self, suite_id: str):
        conn = Tortoise.get_connection('report')
        sql = "SELECT * FROM testcasemodel WHERE suits_id = $1"
        return await conn.execute_query_dict(sql, [suite_id, ])