from fastapi import HTTPException
from tortoise import Tortoise

from .model import SpaceModel
from .dto import *
from .utils import translate
from . import queries, stats
from ..spacesuser.model import SpacesUserModel, SpacesUserRole
from ..users.model import UserModel
import logging
logger = logging.getLogger(__name__)


class SpaceService:
    model = SpaceModel()

    # ─── Delegates to queries ────────────────────────────────────────────────
    get_space_by_id = staticmethod(queries.get_space_by_id)
    get_user_for_space = staticmethod(queries.get_user_for_space)
    get_user_for_filterV2 = staticmethod(queries.get_user_for_filterV2)
    get_space = staticmethod(queries.get_space)
    get_by_short_name = staticmethod(queries.get_by_short_name)
    check_short_name = staticmethod(queries.check_short_name)

    # ─── Delegates to stats ──────────────────────────────────────────────────
    get_all_runs_spaces = staticmethod(stats.get_all_runs_spaces)
    get_statistic_for_space = staticmethod(stats.get_statistic_for_space)
    get_statistic_for_space_old = staticmethod(stats.get_statistic_for_space_old)
    get_bugs_count = staticmethod(stats.get_bugs_count)
    get_pads_count = staticmethod(stats.get_pads_count)
    get_runs_statistic = staticmethod(stats.get_runs_statistic)
    get_arg = staticmethod(stats.get_arg)

    async def create_space(self, space: CreateSpaceDto, user: dict):
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
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            sort = 10

        temp = await self.model.create(
            name=space.name,
            sort=int(sort),
            company_id=this_user.get('company_id'),
            short_name=space.short_name,
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
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            try:
                if len(space_name) > 2:
                    this_space_name = await translate(
                        f"{space_name[0].upper()}{space_name[int(len(space_name) / 2)].upper()}")
            except Exception as e:
                logger.error('Unexpected error: %s', e, exc_info=True)
                this_space_name = await translate(space_name.upper())

        try:
            temp = await SpaceModel.filter(short_name=this_space_name).get()

            if temp.short_name:
                this_space_name = f"{this_space_name}{(await SpaceModel.filter(id=space_id).get()).sort}"
                return this_space_name.replace('0', '')
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            return this_space_name

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
    async def add_user_space(space_id: str, dto: AddUserSpaceDto, user: dict):
        temp_user = await UserModel.filter(mail=dto.mail).first()

        if not temp_user:
            raise HTTPException(status_code=404, detail="user not found")

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
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            try:
                if temp.get('role') == 'company_admin':
                    return True
                else:
                    raise HTTPException(status_code=403, detail="not have rule")
            except Exception as e:
                logger.error('Unexpected error: %s', e, exc_info=True)
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
