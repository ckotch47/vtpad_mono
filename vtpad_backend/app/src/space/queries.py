import json
from fastapi import HTTPException
from tortoise import Tortoise
from ..spacesuser.model import SpacesUserModel, SpacesUserRole
import logging
logger = logging.getLogger(__name__)
async def get_space_by_id(user: dict, space_id: str):
    # todo add owner user and rigth for user
    conn = Tortoise.get_connection("default")
    sql = f'SELECT spacemodel.*, su."right", su."role" FROM spacemodel ' \
          f'LEFT JOIN spacesusermodel su on (su."spaceId" = $2 AND su."userId" = $1) ' \
          f'WHERE spacemodel.id = $2'
    temp = (await conn.execute_query_dict(sql, [user.get('id'), space_id]))[0]

    try:
        temp['right'] = json.loads(temp['right'])
        return temp
    except Exception as e:
        logger.error('Unexpected error: %s', e, exc_info=True)
        return temp
async def get_user_for_space(space_id: str):
    conn = Tortoise.get_connection("default")

    temp = await conn.execute_query_dict(
        'SELECT "userId" as id, "spaceId", role, "right", username, mail, '
        '(avatar_id, filepath) as avatar '
        'FROM spacesusermodel '
        'LEFT JOIN usermodel on spacesusermodel."userId" = usermodel.id '
        'LEFT JOIN filemodel f on usermodel.avatar_id = f.id '
        'WHERE spacesusermodel."spaceId" = $1 '
        'ORDER BY spacesusermodel.role DESC',
        [space_id])
    for i in temp:
        i['right'] = json.loads(i['right'])
        tmp = i['avatar']
        i['avatar'] = {
            'id': tmp[0],
            'filepath': tmp[1]
        }

    return temp
async def get_user_for_filterV2(space_id: str):
    conn = Tortoise.get_connection('default')
    sql = """
        SELECT usermodel.id,  username, mail, (avatar_id, f.filepath) as avatar FROM usermodel
        LEFT JOIN filemodel f on usermodel.avatar_id = f.id
        WHERE usermodel.id IN (SELECT DISTINCT u.id FROM bugsmodel
                                LEFT JOIN usermodel u on u.id = bugsmodel.assigner_id
                                WHERE bugsmodel.spaces_id = $1)
        OR usermodel.id IN (SELECT DISTINCT u.id FROM bugsmodel
                                LEFT JOIN usermodel u on u.id = bugsmodel.create_user_id
                                WHERE bugsmodel.spaces_id = $1)
        OR usermodel.id IN (SELECT DISTINCT u.id FROM bugsmodel
                    LEFT JOIN spacesusermodel sp on sp."spaceId" = $1
                    LEFT JOIN usermodel u on u.id = sp."userId"
                    WHERE bugsmodel.spaces_id = $1);
    """
    return await conn.execute_query_dict(sql, [space_id])

async def get_space(user: dict, order='ASC'):
    conn = Tortoise.get_connection("default")
    order_direction = order.upper() if order.upper() in ('ASC', 'DESC') else 'ASC'
    sql = 'SELECT "spaceId" as id, role, name, sort, short_name FROM spacesusermodel ' \
          'LEFT JOIN spacemodel s on spacesusermodel."spaceId" = s.id ' \
          'WHERE spacesusermodel."userId" = $1 ORDER BY s.sort ' + order_direction
    temp = await conn.execute_query_dict(sql, [user.get('id')])
    return temp
async def get_by_short_name(short_name:str, user: dict):
    conn = Tortoise.get_connection('default')
    sql = """
        SELECT spacemodel.* FROM spacemodel
        LEFT JOIN companymodel c on spacemodel.company_id = c.id
        WHERE c.id = $1
        AND spacemodel.short_name = $2
    """
    result = await conn.execute_query_dict(sql, [user.get('company'), short_name])
    if not result:
        raise HTTPException(status_code=404, detail="not found")
    return result[0]
async def check_short_name(short_name: str, space_id: str, company_id: str):
    conn = Tortoise.get_connection('default')
    sql = """
        SELECT array_agg(short_name) FROM spacemodel
        LEFT JOIN companymodel c on spacemodel.company_id = c.id
        AND c.id = $1
    """
    tmp = (await conn.execute_query_dict(sql, [company_id,]))[0]
    tmp_array = tmp.get('array_agg')
    if short_name and short_name not in tmp_array:
        return True
    raise HTTPException(status_code=403, detail="short name is used")
