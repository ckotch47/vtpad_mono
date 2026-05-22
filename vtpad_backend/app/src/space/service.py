import json

from fastapi import HTTPException
from tortoise import Tortoise

from .model import SpaceModel
from .dto import *

from ..pad.model import PadModel
from ..pad.service import PadService
from ..run.service import RunService
from ..runitems import RunItemsService
from ..spacesuser.model import SpacesUserModel, SpacesUserRole
from ..users.model import UserModel
from ..run.model import RunModel


async def translate(name):
    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ja', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CZ', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA'}

    for key in slovar:
        name = name.replace(key, slovar[key])
    return name


class SpaceService:
    model = SpaceModel()

    async def create_space(self, space: CreateSpaceDto, user: dict):
        # this_user = await UserModel.filter(id=user.get('id')).get_or_none()
        conn = Tortoise.get_connection('default')
        sql = """
            SELECT usermodel.id as id, u.role as company_role, u.company_id FROM usermodel
            LEFT JOIN usercompanysettingsmodel u on usermodel.id = u.user_id
            WHERE usermodel.id = $1
            and u.status = 'active'
        """
        this_user = (await conn.execute_query_dict(sql, [user.get('id')]))[0]
        if not this_user or this_user.get('company_role') != 'company_admin':
            return None

        try:
            last_sort = await SpaceService.get_space(user, 'DESC')
            last_sort = last_sort[0].get('sort')
            sort = ((last_sort / 10) + 1) * 10
        except Exception:
            sort = 10

        temp = await self.model.create(
            name=space.name,
            sort=int(sort),
            company_id=this_user.get('company_id')
        )

        await SpacesUserModel.create(
            userId=this_user.get('id'),
            spaceId=temp.id,
            role=SpacesUserRole.owner)
        return temp

    @staticmethod
    async def generate_short_name(space_name: str, space_id):
        this_space_name = None
        try:
            this_space_name = await translate(
                f"{space_name.split(' ')[0][0].upper()}{space_name.split(' ')[1][0].upper()}")
        except Exception:
            try:
                if len(space_name) > 2:
                    this_space_name = await translate(
                        f"{space_name[0].upper()}{space_name[int(len(space_name) / 2)].upper()}")
            except Exception:
                this_space_name = await translate(space_name.upper())

        try:
            temp = await SpaceModel.filter(short_name=this_space_name).get()

            if temp.short_name:
                this_space_name = f"{this_space_name}{(await SpaceModel.filter(id=space_id).get()).sort}"
                return this_space_name.replace('0', '')
        except Exception:
            return this_space_name

    @staticmethod
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
        except Exception:
            return temp

    @staticmethod
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

    @staticmethod
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
    @staticmethod
    async def get_space(user: dict, order='ASC'):
        conn = Tortoise.get_connection("default")
        order_direction = order.upper() if order.upper() in ('ASC', 'DESC') else 'ASC'
        sql = 'SELECT "spaceId" as id, role, name, sort, short_name FROM spacesusermodel ' \
              'LEFT JOIN spacemodel s on spacesusermodel."spaceId" = s.id ' \
              'WHERE spacesusermodel."userId" = $1 ORDER BY s.sort ' + order_direction
        temp = await conn.execute_query_dict(sql, [user.get('id')])
        return temp

    @staticmethod
    async def update_space(space_id: str, space: UpdateSpaceDto, user: dict):
        this_space = await SpaceModel.filter(id=space_id).get()
        short_name = this_space.short_name

        if space.short_name:
            short_name = str(space.short_name).upper()

        if not short_name:
            short_name = await SpaceService.generate_short_name(space.name, space_id)

        await SpaceService.check_short_name(short_name, space_id, user.get('company'))

        return bool(await SpaceModel.filter(id=space_id).update(name=space.name, short_name=short_name))

    @staticmethod
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

    @staticmethod
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


    @staticmethod
    async def add_user_space(space_id: str, dto: AddUserSpaceDto, user: dict):
        temp_user = await UserModel.filter(mail=dto.mail).first()

        if not temp_user.id:
            return None

        temp = await SpacesUserModel.filter(userId=temp_user.id, spaceId=space_id)
        if temp:
            return None

        await SpacesUserModel.create(
            userId=temp_user.id,
            spaceId=space_id,
            role=SpacesUserRole.collaborator)

        return await SpaceService.get_user_for_space(space_id)

    @staticmethod
    async def delete_space(space_id: str):
        temp = bool(await SpaceModel.filter(id=space_id).delete())
        await SpacesUserModel.filter(spaceId=space_id).delete()
        # todo delete all data from space
        return temp

    @staticmethod
    async def delete_user_from_space(user_id: str, space_id: str, user: dict):
        if user.get('id') == user_id:
            raise HTTPException(status_code=403, detail="not delete self")

        space = await SpacesUserModel.filter(userId=user_id, spaceId=space_id).get()
        if space.role == SpacesUserRole.owner and user.get('role') != 'company_admin':
            raise HTTPException(status_code=403, detail="not delete owner")

        await SpacesUserModel.filter(userId=user_id, spaceId=space_id).delete()
        return await SpaceService.get_user_for_space(space_id)

    @staticmethod
    async def check_owner(user_payload: dict, space_id: str):
        conn = Tortoise.get_connection('default')
        sqlV2 = """
            SELECT spacesusermodel.role as sp_role, u.role as company_role
            FROM spacesusermodel
            LEFT OUTER JOIN usercompanysettingsmodel u on u.user_id = $1
            WHERE "userId" = $1
                AND "spaceId" = $2
                AND u.status = 'active'
            """
        sql_check_role_company_admin = """
            SELECT usercompanysettingsmodel.role FROM usercompanysettingsmodel
            LEFT JOIN spacemodel s on usercompanysettingsmodel.company_id = s.company_id
            WHERE user_id = $1
            AND s.id = $2
        """

        temp = (await conn.execute_query_dict(sqlV2, [user_payload.get('id'), space_id]))[0]
        try:
            if temp.get('sp_role') != SpacesUserRole.owner:
                    raise HTTPException(status_code=403, detail="not have rule")
            else:
                return True
        except Exception:
            try:
                # role = (await conn.execute_query_dict(sql_check_role_company_admin, [user_payload.get('id'), space_id]))[0]
                if temp.get('role') == 'company_admin':
                    return True
                else:
                    raise HTTPException(status_code=403, detail="not have rule")
            except Exception:
                raise HTTPException(status_code=403, detail="not have rule")
    @staticmethod
    async def update_user_rules_in_space(space_id: str, user_id: str, dto: UpdateUserRulesForSpaceDto):
        temp: dict = (await SpacesUserModel.filter(spaceId=space_id, userId=user_id).get()).right

        if dto.editPads is not None:
            temp['editPads'] = dto.editPads
        if dto.editRuns is not None:
            temp['editRuns'] = dto.editRuns
        if dto.editItems is not None:
            temp['editItems'] = dto.editItems
        if dto.editNotes is not None:
            temp['editNotes'] = dto.editNotes
        if dto.closeBugs is not None:
            temp['closeBugs'] = dto.closeBugs
        if dto.editTags is not None:
            temp['editTags'] = dto.editTags

        await SpacesUserModel.filter(spaceId=space_id, userId=user_id).update(right=temp)
        return await SpaceService.get_user_for_space(space_id)

    @staticmethod
    async def make_user_owner_to_space(space_id: str, user_id: str):
        await SpacesUserModel.filter(spaceId=space_id, userId=user_id).update(role=SpacesUserRole.owner)
        return await SpaceService.get_user_for_space(space_id)

    @staticmethod
    async def get_all_runs_spaces(space_id):
        conn = Tortoise.get_connection('default')
        space = await SpaceService.get_space_by_id({}, space_id)

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
            "space_id": space.id,
            "space_name": space.name,
            "pad": res
        }

    @staticmethod
    async def get_statistic_for_space(space_id: str):
        conn = Tortoise.get_connection('default')

        sql_pads = "SELECT count(DISTINCT padmodel.id) as count, count(i.id) as items_count FROM padmodel \
                    LEFT OUTER JOIN itemsmodel i on padmodel.id = i.pad_id \
                    WHERE spaces_id = $1"

        sql_runs_state = "SELECT count(r.id) as item_count, r.state FROM runmodel \
                    LEFT JOIN padmodel p on p.id = runmodel.pads_id \
                    LEFT JOIN runitemsmodel r on runmodel.id = r.run_id \
                    WHERE p.spaces_id = $1 \
                    GROUP BY r.state;"

        sql_all_runs = "SELECT count(runmodel.id) FROM runmodel \
                        LEFT JOIN padmodel p on p.id = runmodel.pads_id \
                        WHERE p.spaces_id = $1;"

        sql_bugs = "SELECT count(bugsmodel.id) as item_count, state FROM bugsmodel \
                    WHERE bugsmodel.spaces_id = $1 \
                    GROUP BY state;"

        sql_all_bugs = "SELECT count(bugsmodel.id) FROM bugsmodel \
                            WHERE bugsmodel.spaces_id = $1;"

        pads = await conn.execute_query_dict(sql_pads, [space_id])

        runs_state = await conn.execute_query_dict(sql_runs_state, [space_id])
        all_runs = await conn.execute_query_dict(sql_all_runs, [space_id])

        bugs = await conn.execute_query_dict(sql_bugs, [space_id])

        all_bugs = await conn.execute_query_dict(sql_all_bugs, [space_id])

        return {
            'pads': pads[0] if pads[0] else 0,
            'runs': {
                'count': SpaceService.get_arg(all_runs, 'count'),
                'state': runs_state
            },
            'bugs': {
                'count': SpaceService.get_arg(all_bugs, 'count'),
                'state': bugs
            }
        }

    @staticmethod
    def get_arg(obj: list, name: str):
        try:
            return obj[0][name]
        except Exception:
            return 0

    @staticmethod
    async def get_statistic_for_space_old(space_id: str):
        return {
            "pads": await SpaceService.get_pads_count(space_id),
            "runs": await SpaceService.get_runs_statistic(space_id),
            "bugs": {
                "count": await SpaceService.get_bugs_count(space_id),
                "open": await SpaceService.get_bugs_count(space_id, 'OPEN'),
                "reopen": await SpaceService.get_bugs_count(space_id, 'REOPEN'),
                "closed": await SpaceService.get_bugs_count(space_id, 'CLOSED'),
                "fixed": await SpaceService.get_bugs_count(space_id, 'FIXED'),
                "hold": await SpaceService.get_bugs_count(space_id, 'HOLD')
            }
        }

    @staticmethod
    async def get_bugs_count(space_id, state=None):
        conn = Tortoise.get_connection('default')
        sql = "SELECT count(id) FROM bugsmodel " \
              "WHERE spaces_id = $1"

        params = [space_id]
        if state:
            ALLOWED_STATES = {'OPEN', 'REOPEN', 'CLOSED', 'FIXED', 'HOLD', 'READY'}
            if state.upper() in ALLOWED_STATES:
                sql += " AND state = $2"
                params.append(state.upper())
        return (await conn.execute_query_dict(sql, params))[0]['count']

    @staticmethod
    async def get_pads_count(space_id):
        temp = await PadModel.filter(spaces_id=space_id)
        count_pad = len(temp)
        return {
            "count": count_pad,
            "items_count": await SpaceService.get_items_count_into_pad(await collect_ids_pad(temp))
        }

    @staticmethod
    async def get_items_count_into_pad(pads_id: list):
        if not pads_id:
            return 0
        conn = Tortoise.get_connection('default')
        sql = "SELECT count(id) FROM itemsmodel WHERE pad_id = ANY($1::uuid[])"
        return (await conn.execute_query_dict(sql, [pads_id]))[0]['count']

    @staticmethod
    async def get_runs_statistic(space_id: str):
        temp_pads = await PadModel.filter(spaces_id=space_id)
        temp_runs = await SpaceService.get_runs_by_pad_ids(await collect_ids_pad(temp_pads))

        temp_runs_ids = await collect_ids_runs(temp_runs)

        runs_count = len(temp_runs)

        return {
            "count": runs_count,
            "items_count": await SpaceService.get_run_items_count_status(temp_runs_ids),
            "passed": await SpaceService.get_run_items_count_status(temp_runs_ids, 'pass'),
            "fail": await SpaceService.get_run_items_count_status(temp_runs_ids, 'fail'),
            "not_status": await SpaceService.get_run_items_count_status(temp_runs_ids, 'null')
        }

    @staticmethod
    async def get_runs_by_pad_ids(pad_ids: list):
        try:
            conn = Tortoise.get_connection('default')
            sql = "SELECT * FROM runmodel WHERE pads_id = ANY($1::uuid[])"
            return await conn.execute_query_dict(sql, [pad_ids])
        except Exception:
            return []

    @staticmethod
    async def get_run_items_count_status(runs_ids: list, state=None):
        try:
            conn = Tortoise.get_connection('default')

            sql = "SELECT count(id) FROM runitemsmodel WHERE run_id = ANY($1::uuid[])"
            params = [runs_ids]
            if state == 'pass' or state == 'fail':
                sql += " AND state = $2"
                params.append(state)
            if state == 'null':
                sql += " AND state is NULL"
            return (await conn.execute_query_dict(sql, params))[0]['count']
        except Exception:
            return 0


async def collect_ids_pad(pad):
    if len(pad) <= 0:
        return []
    res = [str(pad.pop().id)]
    for i in pad:
        res.append(str(i.id))
    return res


async def collect_ids_runs(runs):
    try:
        return [str(i['id']) for i in runs]
    except Exception:
        return []

