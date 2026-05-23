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
    async def get_bugs_with_filter(b_filter: GetBugsDto):
        ALLOWED_ORDER_BY = {
            'id', 'create_date', 'estimate_date', 'short_name',
            'state', 'update_date', 'title', 'assigner_id', 'create_user_id'
        }
        ALLOWED_ORDER_ARROW = {'ASC', 'DESC'}

        str_q = "SELECT \
                bugsmodel.id, \
                bugsmodel.create_date, \
                bugsmodel.estimate_date, \
                bugsmodel.short_name, \
                bugsmodel.state, \
                bugsmodel.update_date,  \
                bugsmodel.title,  \
                bugsmodel.external_link,  \
                bugsmodel.create_user_id, " \
                " json_build_object( \
                    'id',create_user.id, \
                    'username',create_user.username, \
                    'mail',create_user.mail, \
                    'avatar', \
                    json_build_object( \
                        'id',create_user.avatar_id, \
                        'filepath',create_avatar.filepath \
                        ) \
                ) as create_user," \
                "bugsmodel.assigner_id, " \
                "json_build_object( \
                    'id',assigner_user.id, \
                    'username',assigner_user.username, \
                    'mail',assigner_user.mail, \
                    'avatar', \
                    json_build_object( \
                        'id',assigner_user.avatar_id, \
                        'filepath',assigner_avatar.filepath \
                        ) \
                ) as assigner_user," \
                "json_agg( \
                    array( \
                        SELECT jsonb_build_object('id', tagmodel.id, 'title',tagmodel.title,'color', tagmodel.color) as tag \
                        FROM tagmodel \
                            LEFT JOIN bugtagsmodel b on tagmodel.id = b.tag_id \
                        WHERE b.bug_id = bugsmodel.id \
                        GROUP BY tagmodel.id \
                        ) \
                ) as tag, " \
                "bugsmodel.spaces_id " \
                "FROM bugsmodel " \
                "LEFT JOIN usermodel create_user on bugsmodel.create_user_id = create_user.id \
                 LEFT JOIN usermodel assigner_user on bugsmodel.assigner_id = assigner_user.id \
                 LEFT JOIN filemodel assigner_avatar on assigner_user.avatar_id = assigner_avatar.id \
                 LEFT JOIN filemodel create_avatar on create_user.avatar_id = create_avatar.id \
                 LEFT JOIN bugtagsmodel bug_tag on bugsmodel.id = bug_tag.bug_id \
                 LEFT JOIN tagmodel t on bug_tag.tag_id = t.id " \
                "WHERE spaces_id = $1 "

        params = [b_filter.space_id]
        param_idx = 1

        def next_param():
            nonlocal param_idx
            param_idx += 1
            return param_idx

        if b_filter.create_date:
            params.append(b_filter.create_date)
            str_q += f"AND DATE(create_date) >= ${next_param()} "

        if b_filter.create_date_end:
            params.append(b_filter.create_date_end)
            str_q += f"AND DATE(create_date) <= ${next_param()} "

        if b_filter.create_user:
            params.append(b_filter.create_user)
            str_q += f"AND create_user_id = ANY(${next_param()}::uuid[]) "

        if b_filter.assigner_id and not b_filter.not_assigner:
            params.append(b_filter.assigner_id)
            str_q += f"AND assigner_id = ANY(${next_param()}::uuid[]) "

        if b_filter.not_assigner and not b_filter.assigner_id:
            str_q += "AND assigner_id is Null "

        if b_filter.state:
            params.append([s.upper() for s in b_filter.state])
            str_q += f"AND state = ANY(${next_param()}::text[]) "

        state_list = b_filter.state or []
        if 'HOLD' not in state_list:
            str_q += "AND state != 'HOLD' "

        if 'CLOSED' not in state_list:
            str_q += "AND state != 'CLOSED' "

        if b_filter.estimate_date:
            params.append(b_filter.estimate_date)
            str_q += f"AND DATE(estimate_date) >= ${next_param()} "

        if b_filter.estimate_date_end:
            params.append(b_filter.estimate_date_end)
            str_q += f"AND DATE(estimate_date) <= ${next_param()} "

        if b_filter.tag:
            params.append(b_filter.tag)
            str_q += f"AND bug_tag.tag_id = ANY(${next_param()}::uuid[]) "

        if b_filter.external_link:
            patterns = [f"%{elem}%" for elem in b_filter.external_link]
            params.append(patterns)
            str_q += f"AND external_link ~~ ANY(${next_param()}::text[]) "

        str_q += "GROUP BY bugsmodel.id, bugsmodel.create_date, bugsmodel.estimate_date, \
                 bugsmodel.short_name, bugsmodel.state, bugsmodel.update_date, bugsmodel.title, \
                 bugsmodel.external_link, bugsmodel.create_user_id, bugsmodel.assigner_id, \
                 bugsmodel.spaces_id, create_user.id, create_avatar.filepath, \
                 assigner_user.id, assigner_avatar.filepath "

        if b_filter.order_by:
            order_by = b_filter.order_by if b_filter.order_by in ALLOWED_ORDER_BY else 'create_date'
            order_arrow = b_filter.order_arrow.upper() if b_filter.order_arrow and b_filter.order_arrow.upper() in ALLOWED_ORDER_ARROW else 'DESC'
            str_q += f"ORDER BY {order_by} {order_arrow} "
        else:
            str_q += 'ORDER BY create_date DESC '

        if b_filter.limit:
            params.append(b_filter.limit)
            str_q += f'LIMIT ${next_param()} '
        else:
            str_q += 'LIMIT ALL '

        skip = b_filter.skip if b_filter.skip else 0
        params.append(skip)
        str_q += f'OFFSET ${next_param()} '

        conn = Tortoise.get_connection("default")
        temp = (await conn.execute_query_dict(str_q, params))
        for i in temp:
            if i.get('create_user_id'):
                i['create_user'] = json.loads(i['create_user'])
            else:
                i['create_user'] = {}

            if i.get('assigner_id'):
                i['assigner_user'] = json.loads(i['assigner_user'])
            else:
                i['assigner_user'] = {}

            i['tag'] = json.loads(i['tag'])[0]
        return temp

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
            except Exception:
                pass
        return await BugsService.get_bug_detail(temp.id)

    @staticmethod
    async def update_bug_v2(dto: UpdateBugDtoV2, bug_id: str, user: dict, background_tasks: BackgroundTasks):
        await BugsService.check_user_update_bug_v2(bug_id, user, dto.state)

        bug = await BugsModel.filter(id=uuid.UUID(bug_id)).get()
        if not bug:
            raise HTTPException(status_code=404, detail="not found")

        tmp = bug

        for i in dto:
            if i[0] != 'tags' and i[1] and i[1] != bug.__getattribute__(i[0]):
                try:
                    await (CommentBugService
                           .create_history(bug_id, user,
                                           json.dumps({'name': i[0], 'from': str(tmp.__getattribute__(i[0])), 'to': str(i[1])})
                                           ))
                except Exception as e:
                    print(e, '1')
                    pass
                bug.__setattr__(i[0], i[1])

                try:
                    if tmp.short_name:
                        BugsService.send_notification_update_bug_v2(tmp, user, i, dto, background_tasks)
                except Exception as e:
                    print(e, '2')
                    pass
            if i[0] == 'tags' and i[1]:
                await BugsService.update_tag_bug_list(i[1], bug_id)
        await bug.save()

        return await BugsService.get_bug_detail(bug.id)

    @staticmethod
    async def update_tag_bug_list(tags: list[str], bug_id: str):
        bug_tags = await BugTagsService.get_tags_fo_bug(bug_id)
        for tag in tags:
            if not list(filter(lambda x: (x['id'] == uuid.UUID(tag)), bug_tags)):
                await BugTagsService.add_bug_tag(bug_id, tag)
        for tag in bug_tags:
            if str(tag.get('id')) not in tags:
                await BugTagsService.delete_tag_from_bug(bug_id, str(tag.get('id')))
        pass

    @staticmethod
    def send_notification_update_bug_v2(tmp: BugsModel, user: dict, i: str, dto: UpdateBugDtoV2,
                                        background_tasks: BackgroundTasks):
        print({
            "space_id": str(tmp.__getattribute__("spaces_id")),
            "bug_id": str(tmp.id),
            "short_name": str(tmp.short_name),
            "changes": {
                "name": str(i[0]),
                "from": str(tmp.__getattribute__(i[0])),
                "to": str(i[1])
            }
        })
        if str(tmp.__getattribute__('assigner_id')) != str(user.get('id')):
            background_tasks.add_task(NotificationService.update_state_bug,
                                      CreateNotificationDto(
                                          user=str(tmp.__getattribute__('assigner_id')),
                                          data={
                                              "space_id": str(tmp.__getattribute__("spaces_id")),
                                              "bug_id": str(tmp.id),
                                              "short_name": str(tmp.short_name),
                                              "changes": {
                                                  "name": str(i[0]),
                                                  "from": str(tmp.__getattribute__(i[0])),
                                                  "to": str(i[1])
                                              }
                                          },
                                          event=EventNotificationEnum.update if not dto.assigner_id else EventNotificationEnum.assign))
        if str(tmp.__getattribute__('create_user_id')) != str(user.get('id')):
            background_tasks.add_task(NotificationService.update_state_bug,
                                      CreateNotificationDto(
                                          user=str(tmp.__getattribute__('create_user_id')),
                                          data={
                                              "space_id": str(tmp.__getattribute__("spaces_id")),
                                              "bug_id": str(tmp.id),
                                              "short_name": str(tmp.short_name),
                                              "changes": {
                                                  "name": str(i[0]),
                                                  "from": str(tmp.__getattribute__(i[0])),
                                                  "to": str(i[1])
                                              }
                                          },
                                          event=EventNotificationEnum.update if not dto.assigner_id else EventNotificationEnum.assign))

    @staticmethod
    async def update_bug(bug: UpdateBugDto, bug_id: str, user: dict, background_tasks: BackgroundTasks):
        if bug.state == StateBugEnum.closed or bug.state == StateBugEnum.hold:
            await BugsService.check_user_for_update_bug_state_open_bug(bug_id, user)

        try:
            estimate_date = bug.estimate_date.replace(hour=23)
        except Exception:
            estimate_date = None

        temp = await BugsModel.filter(id=uuid.UUID(bug_id)).get()
        tmp1 = temp
        await BugsModel.filter(id=uuid.UUID(bug_id)).update(
            update_date=datetime.now(),
            title=bug.title,
            steps=bug.steps,
            text=bug.text,
            state=bug.state,
            assigner_id=bug.assigner,
            additional_link=bug.additional_link,
            estimate_date=estimate_date,
            external_link=bug.external_link
        )
        # add comment for change
        # todo rework history comment
        try:
            if bug.title != '' and str(temp.title) != bug.title:
                await CommentBugService.create_history(bug_id, user,
                                                       f"<p>change title</p> <s>{temp.title}</s> to {bug.title}<hr>")
            if bug.text != '<p></p>' and str(temp.text) != bug.text:
                await CommentBugService.create_history(bug_id, user,
                                                       f"<p>change text</p> <s>{temp.text}</s> to {bug.text}<hr>")
            if bug.steps != '<p></p>' and str(temp.steps) != bug.steps:
                await CommentBugService.create_history(bug_id, user,
                                                       f"<p>change steps</p> <s>{temp.steps}</s> to {bug.steps}<hr>")
            if bug.additional_link != '<p></p>' and str(temp.additional_link) != bug.additional_link:
                await CommentBugService.create_history(bug_id, user,
                                                       f"<p>change additional link</p> <s>{temp.additional_link}</s> to {bug.additional_link}<hr>")
        except Exception:
            pass
        # todo rework
        if str(bug.assigner) != str(temp.assigner) and str(bug.assigner) != str(user.get('id')):
            try:
                background_tasks.add_task(NotificationService.add_notification_assign,
                                          CreateNotificationDto(
                                              user=str(bug.assigner),
                                              data=f'You assigner bug {temp.short_name} <a href="/space/{temp.spaces_id}#bugs?shortName={temp.short_name}">{temp.short_name}</a>',
                                              event=EventNotificationEnum.assign))
            except Exception:
                pass

        if bug.state != temp.state:
            try:
                if str(bug.assigner) != str(user.get('id')):
                    background_tasks.add_task(NotificationService.update_state_bug,
                                              CreateNotificationDto(
                                                  user=str(bug.assigner),
                                                  data=f'Update bug {temp.short_name} <a href="/space/{temp.spaces_id}#bugs?shortName={temp.short_name}">{temp.short_name}</a>',
                                                  event=EventNotificationEnum.update))

                if str(temp.create_user_id) != str(user.get('id')):
                    background_tasks.add_task(NotificationService.update_state_bug,
                                              CreateNotificationDto(
                                                  user=str(temp.create_user_id),
                                                  data=f'Update bug {temp.short_name} <a href="/space/{temp.spaces_id}#bugs?shortName={temp.short_name}">{temp.short_name}</a>',
                                                  event=EventNotificationEnum.update))
            except Exception:
                pass

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
                except Exception:
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
        except Exception:
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
        except Exception:
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
        except Exception:
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
    async def get_bug_detail_by_short_name(space_id: uuid.UUID, short_name: str):
        temp = await BugsModel.filter(spaces_id=str(space_id), short_name=short_name).get_or_none()
        if not temp:
            raise HTTPException(status_code=404, detail="Not found")
        return await BugsService.get_bug_detail(bug_id=str(temp.id))

    @staticmethod
    async def get_id_by_short_name(space_id: uuid.UUID, short_name: str):
        temp = await BugsModel.filter(short_name=short_name, spaces_id=space_id).get_or_none()
        if not temp:
            raise HTTPException(status_code=404, detail="Not found")
        return temp.id

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
                LEFT JOIN spacemodel s on s.id = bugsmodel.spaces_id \
                LEFT JOIN usercompanysettingsmodel u3 on u3.user_id = $2 \
            WHERE bugsmodel.short_name = $1 \
            AND u3.status = 'active' \
            group by bugsmodel.id, u.id, f.id, u2.id, f2.id, u3.id;"
        try:
            bug = (await conn.execute_query_dict(sql, [short_name, user_payload.get('id')]))[0]

            bug.update({'tag': await BugTagsService.get_tags_fo_bug(bug.get('id'))})
            bug.update({'external_link': parse_external_link(bug.get('external_link'))})

            if bug.get('assigner_id'):
                bug['assigner_user'] = json.loads(bug['assigner_user'])
            else:
                bug['assigner_user'] = {}

            bug['create_user'] = json.loads(bug['create_user'])

            return bug
        except Exception:
            raise HTTPException(status_code=404, detail="not found")
