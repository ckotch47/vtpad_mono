from tortoise import Tortoise

from app.src.bug import BugsModel
from .dto import *


class QAReportService:
    def __init__(self):
        self.bugsModel = BugsModel()

    async def get_bugs_list(self, dto: GetBugsDto):
        sql_created = "SELECT id, create_date, update_date, title, short_name, state, spaces_id, create_user_id FROM bugsmodel \
                WHERE spaces_id = $1 \
                AND create_date >= $2 \
                AND create_date <= $3 \
                AND create_user_id = $4 \
                ORDER BY state DESC "

        sql_updated = "SELECT id, create_date, update_date, title, short_name, state, spaces_id, create_user_id FROM bugsmodel \
                WHERE spaces_id = $1 \
                AND update_date >= $2 \
                AND update_date <= $3 \
                AND create_user_id = $4 \
                AND DATE_TRUNC('second', update_date) != DATE_TRUNC('second', create_date) \
                AND state != 'OPEN' \
                ORDER BY state DESC"
        conn = Tortoise.get_connection('default')
        params = [dto.space_id, dto.date_start, dto.date_end, dto.create_user]
        opened = await conn.execute_query_dict(sql_created, params)
        updated = await conn.execute_query_dict(sql_updated, params)
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
        sql = "SELECT DISTINCT create_user_id, u.username, u.mail from bugsmodel \
                LEFT JOIN usermodel u on bugsmodel.create_user_id = u.id \
                WHERE spaces_id = $1"
        conn = Tortoise.get_connection('default')
        return await conn.execute_query_dict(sql, [space_id])
