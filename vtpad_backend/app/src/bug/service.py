import datetime
import json
import uuid
from typing import List

from fastapi import HTTPException, BackgroundTasks
from tortoise import Tortoise

from .enum import StateBugEnum
from .model import BugsModel
from .dto import *

from ..notification.dto import CreateNotificationDto
from ..notification.enum import EventNotificationEnum
from ..space import SpaceModel
from ..space.service import SpaceService
from ..spacesuser.model import SpacesUserRole
from ..bugtags.service import BugTagsService
from ..tag.service import TagService
from datetime import datetime

from ..notification.service import NotificationService
from ..comments.service import CommentBugService
import logging
logger = logging.getLogger(__name__)


def parse_external_link(link: str):
    return link
    if type(link) != str:
        return None
    if link.find('app.clickup.com') > -1:
        temp = link.split('/')
        return {
            "link": link,
            "task": temp[len(temp) - 1]
        }
    return {
        "link": link,
        "task": None
    }


class BugsService:
    tag_service = TagService()
    @staticmethod
    def _get_bug_select_sql():
        return (
            "SELECT "
            "bugsmodel.id, bugsmodel.create_date, bugsmodel.estimate_date, "
            "bugsmodel.short_name, bugsmodel.state, bugsmodel.update_date, "
            "bugsmodel.title, bugsmodel.external_link, bugsmodel.create_user_id, "
            "json_build_object("
            "'id',create_user.id, 'username',create_user.username, 'mail',create_user.mail, "
            "'avatar', json_build_object('id',create_user.avatar_id, 'filepath',create_avatar.filepath)"
            ") as create_user, "
            "bugsmodel.assigner_id, "
            "json_build_object("
            "'id',assigner_user.id, 'username',assigner_user.username, 'mail',assigner_user.mail, "
            "'avatar', json_build_object('id',assigner_user.avatar_id, 'filepath',assigner_avatar.filepath)"
            ") as assigner_user, "
            "json_agg(array("
            "SELECT jsonb_build_object('id', tagmodel.id, 'title',tagmodel.title,'color', tagmodel.color) "
            "FROM tagmodel LEFT JOIN bugtagsmodel b on tagmodel.id = b.tag_id "
            "WHERE b.bug_id = bugsmodel.id GROUP BY tagmodel.id"
            ")) as tag, bugsmodel.spaces_id "
            "FROM bugsmodel "
            "LEFT JOIN usermodel create_user on bugsmodel.create_user_id = create_user.id "
            "LEFT JOIN usermodel assigner_user on bugsmodel.assigner_id = assigner_user.id "
            "LEFT JOIN filemodel assigner_avatar on assigner_user.avatar_id = assigner_avatar.id "
            "LEFT JOIN filemodel create_avatar on create_user.avatar_id = create_avatar.id "
            "LEFT JOIN bugtagsmodel bug_tag on bugsmodel.id = bug_tag.bug_id "
            "LEFT JOIN tagmodel t on bug_tag.tag_id = t.id "
            "WHERE spaces_id = $1 "
        )

    @staticmethod
    def _apply_bug_filters(sql, params, b_filter):
        param_idx = 1

        def next_param():
            nonlocal param_idx
            param_idx += 1
            return param_idx

        if b_filter.create_date:
            params.append(b_filter.create_date)
            sql += f"AND DATE(create_date) >= ${next_param()} "

        if b_filter.create_date_end:
            params.append(b_filter.create_date_end)
            sql += f"AND DATE(create_date) <= ${next_param()} "

        if b_filter.create_user:
            params.append(b_filter.create_user)
            sql += f"AND create_user_id = ANY(${next_param()}::uuid[]) "

        if b_filter.assigner_id and not b_filter.not_assigner:
            params.append(b_filter.assigner_id)
            sql += f"AND assigner_id = ANY(${next_param()}::uuid[]) "

        if b_filter.not_assigner and not b_filter.assigner_id:
            sql += "AND assigner_id is Null "

        if b_filter.state:
            params.append([s.upper() for s in b_filter.state])
            sql += f"AND state = ANY(${next_param()}::text[]) "

        state_list = b_filter.state or []
        if 'HOLD' not in state_list:
            sql += "AND state != 'HOLD' "
        if 'CLOSED' not in state_list:
            sql += "AND state != 'CLOSED' "

        if b_filter.estimate_date:
            params.append(b_filter.estimate_date)
            sql += f"AND DATE(estimate_date) >= ${next_param()} "

        if b_filter.estimate_date_end:
            params.append(b_filter.estimate_date_end)
            sql += f"AND DATE(estimate_date) <= ${next_param()} "

        if b_filter.tag:
            params.append(b_filter.tag)
            sql += f"AND bug_tag.tag_id = ANY(${next_param()}::uuid[]) "

        if b_filter.external_link:
            patterns = [f"%{elem}%" for elem in b_filter.external_link]
            params.append(patterns)
            sql += f"AND external_link ~~ ANY(${next_param()}::text[]) "

        if b_filter.q:
            params.append(f"%{b_filter.q}%")
            p = next_param()
            sql += f"AND (bugsmodel.title ILIKE ${p} OR bugsmodel.short_name ILIKE ${p}) "

        return sql

    @staticmethod
    def _apply_bug_grouping(sql):
        return sql + (
            "GROUP BY bugsmodel.id, bugsmodel.create_date, bugsmodel.estimate_date, "
            "bugsmodel.short_name, bugsmodel.state, bugsmodel.update_date, bugsmodel.title, "
            "bugsmodel.external_link, bugsmodel.create_user_id, bugsmodel.assigner_id, "
            "bugsmodel.spaces_id, create_user.id, create_avatar.filepath, "
            "assigner_user.id, assigner_avatar.filepath "
        )

    @staticmethod
    def _apply_bug_ordering(sql, b_filter):
        ALLOWED_ORDER_BY = {
            'id', 'create_date', 'estimate_date', 'short_name',
            'state', 'update_date', 'title', 'assigner_id', 'create_user_id'
        }
        ALLOWED_ORDER_ARROW = {'ASC', 'DESC'}

        if b_filter.order_by:
            order_by = b_filter.order_by if b_filter.order_by in ALLOWED_ORDER_BY else 'create_date'
            order_arrow = b_filter.order_arrow.upper() if b_filter.order_arrow and b_filter.order_arrow.upper() in ALLOWED_ORDER_ARROW else 'DESC'
            sql += f"ORDER BY {order_by} {order_arrow} "
        else:
            sql += 'ORDER BY create_date DESC '
        return sql

    @staticmethod
    def _apply_bug_pagination(sql, params, b_filter):
        param_idx = len(params)

        def next_param():
            nonlocal param_idx
            param_idx += 1
            return param_idx

        if b_filter.limit:
            params.append(b_filter.limit)
            sql += f'LIMIT ${next_param()} '
        else:
            sql += 'LIMIT ALL '

        skip = b_filter.skip if b_filter.skip else 0
        params.append(skip)
        sql += f'OFFSET ${next_param()} '
        return sql

    @staticmethod
    def _serialize_bug_rows(rows):
        for row in rows:
            if row.get('create_user_id'):
                row['create_user'] = json.loads(row['create_user'])
            else:
                row['create_user'] = {}

            if row.get('assigner_id'):
                row['assigner_user'] = json.loads(row['assigner_user'])
            else:
                row['assigner_user'] = {}

            row['tag'] = json.loads(row['tag'])[0]
        return rows

    @staticmethod
    async def get_bugs_with_filter(b_filter: GetBugsDto):
        params = [b_filter.space_id]
        sql = BugsService._get_bug_select_sql()
        sql = BugsService._apply_bug_filters(sql, params, b_filter)
        sql = BugsService._apply_bug_grouping(sql)
        sql = BugsService._apply_bug_ordering(sql, b_filter)
        sql = BugsService._apply_bug_pagination(sql, params, b_filter)

        conn = Tortoise.get_connection("default")
        rows = await conn.execute_query_dict(sql, params)
        return BugsService._serialize_bug_rows(rows)

    @staticmethod
    async def get_bug_detail(bug_id: str, user: dict = None):
        conn = Tortoise.get_connection("default")

        sql_new = "SELECT bugsmodel.*, \
                       jsonb_build_object('id', u.id, 'mail', u.mail, 'username', u.username, 'avatar', \
                                          jsonb_build_object('id', f.id, 'filepath', f.filepath))   as assigner_user, \
                       jsonb_build_object('id', u2.id, 'mail', u2.mail, 'username', u2.username, 'avatar', \
                                          jsonb_build_object('id', f2.id, 'filepath', f2.filepath)) as create_user \
                FROM bugsmodel \
                         LEFT JOIN usermodel u on bugsmodel.assigner_id = u.id \
                         LEFT JOIN usermodel u2 on u2.id = bugsmodel.create_user_id \
                         LEFT JOIN filemodel f on u.avatar_id = f.id \
                         LEFT JOIN filemodel f2 on u2.avatar_id = f2.id \
                WHERE bugsmodel.id = $1";
        result = await conn.execute_query_dict(sql_new, [bug_id])
        if not result:
            raise HTTPException(status_code=404, detail="not found")
        bug = result[0]

        bug.update({'tag': await BugTagsService.get_tags_fo_bug(bug_id)})
        bug.update({'external_link': parse_external_link(bug.get('external_link'))})

        if bug.get('assigner_id'):
            bug['assigner_user'] = json.loads(bug['assigner_user'])
        else:
            bug['assigner_user'] = {}

        bug['create_user'] = json.loads(bug['create_user'])

        return bug

    @staticmethod
    async def create_bug(bug: CreateBugDto, user: dict, background_tasks: BackgroundTasks):
        short_name = await BugsService.generate_short_name(str(bug.space_id))
        temp = await BugsModel.create(
            create_user_id=user.get('id'),
            title=bug.title,
            text=bug.text,
            steps=bug.steps,
            additional_link=bug.additional_link,
            assigner_id=bug.assigner,
            spaces_id=bug.space_id,
            state=bug.state,
            estimate_date=bug.estimate_date,
            short_name=short_name,
            external_link=bug.external_link
        )
        # todo rewort
        # todo rework history comment
        if bug.assigner:
            try:
                background_tasks.add_task(NotificationService.add_notification_assign,
                                          CreateNotificationDto(
                                              user=str(bug.assigner),
                                              data=f'You assigner bug {temp.short_name} <a href="/space/{temp.spaces_id}#bugs?shortName={temp.short_name}">{temp.short_name}</a>',
                                              event=EventNotificationEnum.assign))
            except Exception as e:
                logger.error('Unexpected error: %s', e, exc_info=True)
        return await BugsService.get_bug_detail(temp.id)

    @staticmethod
    def _build_bug_change_payload(tmp: BugsModel, field_name: str, new_value):
        return {
            "space_id": str(tmp.spaces_id),
            "bug_id": str(tmp.id),
            "short_name": str(tmp.short_name),
            "changes": {
                "name": field_name,
                "from": str(getattr(tmp, field_name, '')),
                "to": str(new_value)
            }
        }

    @staticmethod
    def _notify_bug_change(tmp: BugsModel, user: dict, field_name: str, new_value, is_assigner_change: bool,
                           background_tasks: BackgroundTasks):
        payload = BugsService._build_bug_change_payload(tmp, field_name, new_value)
        event = EventNotificationEnum.assign if is_assigner_change else EventNotificationEnum.update

        if str(tmp.assigner_id) != str(user.get('id')):
            background_tasks.add_task(
                NotificationService.update_state_bug,
                CreateNotificationDto(
                    user=str(tmp.assigner_id),
                    data=payload,
                    event=event))
        if str(tmp.create_user_id) != str(user.get('id')):
            background_tasks.add_task(
                NotificationService.update_state_bug,
                CreateNotificationDto(
                    user=str(tmp.create_user_id),
                    data=payload,
                    event=event))

    @staticmethod
    async def _apply_field_updates(bug, bug_id, user, tmp, dto, background_tasks):
        for field_name, new_value in dto:
            if field_name != 'tags' and new_value and new_value != getattr(bug, field_name, None):
                try:
                    await CommentBugService.create_history(
                        bug_id, user,
                        json.dumps({'name': field_name, 'from': str(getattr(tmp, field_name, '')), 'to': str(new_value)}))
                except Exception as e:
                    logger.error(e, exc_info=True)
                    pass
                setattr(bug, field_name, new_value)
                try:
                    if tmp.short_name:
                        BugsService._notify_bug_change(tmp, user, field_name, new_value, bool(dto.assigner_id), background_tasks)
                except Exception as e:
                    logger.error(e, exc_info=True)
                    pass

    @staticmethod
    async def update_bug_v2(dto: UpdateBugDtoV2, bug_id: str, user: dict, background_tasks: BackgroundTasks):
        await BugsService.check_user_update_bug_v2(bug_id, user, dto.state)

        bug = await BugsModel.filter(id=uuid.UUID(bug_id)).get()
        if not bug:
            raise HTTPException(status_code=404, detail="not found")

        tmp = bug
        await BugsService._apply_field_updates(bug, bug_id, user, tmp, dto, background_tasks)

        if dto.tags:
            await BugsService.update_tag_bug_list(dto.tags, bug_id)

        await bug.save()
        return await BugsService.get_bug_detail(bug.id)

    @staticmethod
    async def update_tag_bug_list(tags: list[str], bug_id: str):
        bug_tags = await BugTagsService.get_tags_fo_bug(bug_id)
        existing_ids = {str(t.get('id')) for t in bug_tags}
        new_ids = set(tags)

        for tag_id in new_ids - existing_ids:
            await BugTagsService.add_bug_tag(bug_id, tag_id)
        for tag in bug_tags:
            if str(tag.get('id')) not in new_ids:
                await BugTagsService.delete_tag_from_bug(bug_id, str(tag.get('id')))

    @staticmethod
    def _prepare_estimate_date(estimate_date):
        try:
            return estimate_date.replace(hour=23)
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            return None

    @staticmethod
    async def _create_bug_history(bug_id, user, old_bug, new_bug):
        try:
            if new_bug.title != '' and str(old_bug.title) != new_bug.title:
                await CommentBugService.create_history(
                    bug_id, user,
                    f"<p>change title</p> <s>{old_bug.title}</s> to {new_bug.title}<hr>")
            if new_bug.text != '<p></p>' and str(old_bug.text) != new_bug.text:
                await CommentBugService.create_history(
                    bug_id, user,
                    f"<p>change text</p> <s>{old_bug.text}</s> to {new_bug.text}<hr>")
            if new_bug.steps != '<p></p>' and str(old_bug.steps) != new_bug.steps:
                await CommentBugService.create_history(
                    bug_id, user,
                    f"<p>change steps</p> <s>{old_bug.steps}</s> to {new_bug.steps}<hr>")
            if new_bug.additional_link != '<p></p>' and str(old_bug.additional_link) != new_bug.additional_link:
                await CommentBugService.create_history(
                    bug_id, user,
                    f"<p>change additional link</p> <s>{old_bug.additional_link}</s> to {new_bug.additional_link}<hr>")
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)

    @staticmethod
    def _send_assign_notification(temp, user, bug, background_tasks):
        if str(bug.assigner_id) != str(temp.assigner) and str(bug.assigner_id) != str(user.get('id')):
            try:
                background_tasks.add_task(
                    NotificationService.add_notification_assign,
                    CreateNotificationDto(
                        user=str(bug.assigner_id),
                        data=f'You assigner bug {temp.short_name} <a href="/space/{temp.spaces_id}#bugs?shortName={temp.short_name}">{temp.short_name}</a>',
                        event=EventNotificationEnum.assign))
            except Exception as e:
                logger.error('Unexpected error: %s', e, exc_info=True)

    @staticmethod
    def _send_state_change_notifications(temp, user, bug, background_tasks):
        if bug.state != temp.state:
            try:
                if str(bug.assigner_id) != str(user.get('id')):
                    background_tasks.add_task(
                        NotificationService.update_state_bug,
                        CreateNotificationDto(
                            user=str(bug.assigner_id),
                            data=f'Update bug {temp.short_name} <a href="/space/{temp.spaces_id}#bugs?shortName={temp.short_name}">{temp.short_name}</a>',
                            event=EventNotificationEnum.update))
                if str(temp.create_user_id) != str(user.get('id')):
                    background_tasks.add_task(
                        NotificationService.update_state_bug,
                        CreateNotificationDto(
                            user=str(temp.create_user_id),
                            data=f'Update bug {temp.short_name} <a href="/space/{temp.spaces_id}#bugs?shortName={temp.short_name}">{temp.short_name}</a>',
                            event=EventNotificationEnum.update))
            except Exception as e:
                logger.error('Unexpected error: %s', e, exc_info=True)

    @staticmethod
    async def update_bug(bug: UpdateBugDto, bug_id: str, user: dict, background_tasks: BackgroundTasks):
        if bug.state == StateBugEnum.closed or bug.state == StateBugEnum.hold:
            await BugsService.check_user_for_update_bug_state_open_bug(bug_id, user)

        estimate_date = BugsService._prepare_estimate_date(bug.estimate_date)
        temp = await BugsModel.filter(id=uuid.UUID(bug_id)).get()

        await BugsModel.filter(id=uuid.UUID(bug_id)).update(
            update_date=datetime.now(),
            title=bug.title,
            steps=bug.steps,
            text=bug.text,
            state=bug.state,
            assigner_id=bug.assigner_id,
            additional_link=bug.additional_link,
            estimate_date=estimate_date,
            external_link=bug.external_link
        )

        await BugsService._create_bug_history(bug_id, user, temp, bug)
        BugsService._send_assign_notification(temp, user, bug, background_tasks)
        BugsService._send_state_change_notifications(temp, user, bug, background_tasks)

        return await BugsService.get_bug_detail(temp.id)


    async def get_filters(self, space_id: str, user: dict):
        enum = []
        for i in StateBugEnum:
            enum.append(i.title().upper())
        return {
            "create_date": True,
            "create_date_end": True,
            "estimate_date": True,
            "estimate_date_end": True,
            "state": enum,
            "user": await SpaceService.get_user_for_filterV2(space_id), # get_user_for_space(space_id),
            "order_by": [
                "id",
                "create_date",
                "update_date",
                "short_name",
                "state",
                "estimate_date",
                "assigner_id",
                "create_user_id",
            ],
            "tag": await self.tag_service.get_tag(space_id),
            "external_link": await BugsService.get_external_link_for_filter_bug(space_id)
        }

    @staticmethod
    async def get_filter_by_row(space_id: str, row: str):
        ALLOWED_ROWS = {'state', 'assigner_id', 'create_user_id', 'tag', 'short_name', 'title', 'external_link'}
        if row not in ALLOWED_ROWS:
            raise HTTPException(status_code=400, detail="invalid row")

        conn = Tortoise.get_connection('default')
        if row == 'state':
            enum = []
            for i in StateBugEnum:
                enum.append(i.title().upper())
            return enum
        if row == 'assigner_id' or row == 'create_user_id':
            sql = 'SELECT DISTINCT "' + row + '" as id, u.username, u.mail, (f.id, f.filepath) as avatar FROM bugsmodel ' \
                  'LEFT JOIN usermodel u on bugsmodel."' + row + '" = u.id ' \
                  "LEFT JOIN filemodel f on u.avatar_id = f.id " \
                  "WHERE spaces_id = $1;"
            temp = await conn.execute_query_dict(sql, [space_id])
            for i in temp:
                try:
                    if i['avatar'][0] is not None:
                        i['avatar'] = {
                            "id": i['avatar'][0],
                            "filepath": i['avatar'][1]
                        }
                    else:
                        i['avatar'] = {}
                except Exception as e:
                    logger.error('Unexpected error: %s', e, exc_info=True)
                    i['avatar'] = {}
            return temp

        if row == 'tag':
            sql = "SELECT * FROM tagmodel WHERE tagmodel.space_id = $1"
            return await conn.execute_query_dict(sql, [space_id])
        sql = 'SELECT DISTINCT "' + row + '" FROM bugsmodel ' \
              "WHERE spaces_id = $1 " \
              'ORDER BY "' + row + '" DESC'
        return await conn.execute_query_dict(sql, [space_id])

    @staticmethod
    async def get_external_link_for_filter_bug(space_id):
        conn = Tortoise.get_connection("default")
        sql = "SELECT DISTINCT external_link FROM bugsmodel " \
              "WHERE spaces_id = $1 " \
              "AND state in ('OPEN', 'REOPEN', 'FIXED') " \
              "AND external_link LIKE '%http%' "
        temp = await conn.execute_query_dict(sql, [space_id])
        res = []
        for i in temp:
            res.append(i['external_link'])
        return res

    @staticmethod
    async def get_create_date_for_filters(space_id):
        temp = await BugsModel.filter(spaces_id=space_id).distinct().order_by('create_date').values_list('create_date')
        res = []
        for i in temp:
            res.append(str(i[0]).split(' ')[0])
        return set(list(res))

    @staticmethod
    async def get_estimate_date_for_filters(space_id):
        temp = await BugsModel.filter(spaces_id=space_id).distinct().order_by('estimate_date').values_list(
            'estimate_date')
        res = []
        for i in temp:
            if i[0]:
                res.append(i[0])
        return res

    @staticmethod
    async def check_user_update_bug_v2(bug_id: str, user: dict, state: StateBugEnum):
        conn = Tortoise.get_connection("default")
        try:
            temp: dict = (await conn.execute_query_dict(
                "SELECT role, \"right\" FROM bugsmodel "
                "LEFT JOIN spacemodel s on bugsmodel.spaces_id = s.id "
                "LEFT JOIN spacesusermodel sp on sp.\"spaceId\" = s.id "
                "WHERE bugsmodel.id = $1 "
                "AND sp.\"userId\" = $2",
                [bug_id, user.get('id')]
            ))[0]
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            raise HTTPException(status_code=403, detail="not have right")

        if temp['role'] == SpacesUserRole.owner:
            return True
        try:
            if state == StateBugEnum.closed or state == StateBugEnum.hold:
                can_close = json.loads(temp['right'])['closeBugs']
                if can_close:
                    return True
                else:
                    raise HTTPException(status_code=403, detail="not have right")
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_user_for_update_bug_state_open_bug(bug_id: str, user: dict):
        # closeBugs
        conn = Tortoise.get_connection("default")
        temp: dict = (await conn.execute_query_dict(
            "SELECT role, \"right\" FROM bugsmodel "
            "LEFT JOIN spacemodel s on bugsmodel.spaces_id = s.id "
            "LEFT JOIN spacesusermodel sp on sp.\"spaceId\" = s.id "
            "WHERE bugsmodel.id = $1 "
            "AND sp.\"userId\" = $2",
            [bug_id, user.get('id')]
        ))[0]

        if temp['role'] == SpacesUserRole.owner:
            return True
        try:
            can_close = json.loads(temp['right'])['closeBugs']

            if can_close:
                return True
            else:
                raise HTTPException(status_code=403, detail="not have right")
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def generate_short_name(space_id: str):
        space = await SpaceModel.filter(id=space_id).get_or_none()
        if not space.short_name:
            return None
        bug_count = await BugsModel.filter(spaces_id=space_id).count()
        if bug_count:
            return f"{space.short_name}-{bug_count}"
        return f"{space.short_name}-0"

    @staticmethod
    async def add_tag_to_bug(bug_id: str, dto: AddTagToBugDto):
        return await BugTagsService.add_bug_tag(bug_id, dto.tag_id)

    @staticmethod
    async def delete_tag_from_bug(bug_id: str, tag_id: str):
        return await BugTagsService.delete_tag_from_bug(bug_id, tag_id)

    @staticmethod
    async def get_detail_by_short_name(short_name: str, user_payload: dict):
        conn = Tortoise.get_connection('default')
        sql = "SELECT bugsmodel.*, \
                   jsonb_build_object('id', u.id, 'mail', u.mail, 'username', u.username, 'avatar', jsonb_build_object('id', f.id, 'filepath', f.filepath))   as assigner_user, \
                   jsonb_build_object('id', u2.id, 'mail', u2.mail, 'username', u2.username, 'avatar', jsonb_build_object('id', f2.id, 'filepath', f2.filepath)) as create_user \
            FROM bugsmodel \
                LEFT JOIN usermodel u on bugsmodel.assigner_id = u.id \
                LEFT JOIN usermodel u2 on u2.id = bugsmodel.create_user_id \
                LEFT JOIN filemodel f on u.avatar_id = f.id \
                LEFT JOIN filemodel f2 on u2.avatar_id = f2.id \
            WHERE bugsmodel.short_name = $1;"
        try:
            bug = (await conn.execute_query_dict(sql, [short_name]))[0]

            bug.update({'tag': await BugTagsService.get_tags_fo_bug(bug.get('id'))})
            bug.update({'external_link': parse_external_link(bug.get('external_link'))})

            if bug.get('assigner_id'):
                bug['assigner_user'] = json.loads(bug['assigner_user'])
            else:
                bug['assigner_user'] = {}

            bug['create_user'] = json.loads(bug['create_user'])

            return bug
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            raise HTTPException(status_code=404, detail="not found")
