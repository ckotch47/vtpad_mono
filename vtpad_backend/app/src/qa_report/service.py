from tortoise import Tortoise

from app.src.bug import BugsModel
from .dto import *


class QAReportService:
    def __init__(self):
        self.bugsModel = BugsModel()

    async def get_bugs_list(self, dto: GetBugsDto):
        sql_created = f"SELECT id, create_date, update_date, title, short_name, state, spaces_id, create_user_id FROM bugsmodel \
                WHERE spaces_id = '{dto.space_id}' \
                AND create_date >= '{dto.date_start}' \
                AND create_date <= '{dto.date_end}' \
                AND create_user_id = '{dto.create_user}' \
                ORDER BY state DESC "

        sql_updated = f"SELECT id, create_date, update_date, title, short_name, state, spaces_id, create_user_id FROM bugsmodel \
                WHERE spaces_id = '{dto.space_id}' \
                AND update_date >= '{dto.date_start}' \
                AND update_date <= '{dto.date_end}' \
                AND create_user_id = '{dto.create_user}' \
                AND DATE_TRUNC('second', update_date) != DATE_TRUNC('second', create_date) \
                AND state != 'OPEN' \
                ORDER BY state DESC"
        conn = Tortoise.get_connection('default')
        opened = await conn.execute_query_dict(sql_created)
        updated = await conn.execute_query_dict(sql_updated)
        print()
        return {
            'opened': opened,
            'updated': updated,
            'count': {
                'opened': len(opened),
                'updated': len(updated),
                'open': len(list(filter(lambda x: (x['state'] == 'OPEN'), opened))),
                'reopen': len(list(filter(lambda x: (x['state'] == 'REOPEN'), opened))),
                'closed': len(list(filter(lambda x: (x['state'] == 'CLOSED'), opened))),
                'fixed': len(list(filter(lambda x: (x['state'] == 'FIXED'), opened))),
                'hold': len(list(filter(lambda x: (x['state'] == 'HOLD'), opened))),
                'ready': len(list(filter(lambda x: (x['state'] == 'READY'), opened)))
            }
        }

    async def get_create_user_list(self, space_id: str):
        sql = f"SELECT DISTINCT create_user_id, u.username, u.mail from bugsmodel \
                LEFT JOIN usermodel u on bugsmodel.create_user_id = u.id \
                WHERE spaces_id = '{space_id}'"
        conn = Tortoise.get_connection('default')
        return await conn.execute_query_dict(sql)
