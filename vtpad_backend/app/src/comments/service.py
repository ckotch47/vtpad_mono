import datetime
import json
import uuid
from typing import Any

from fastapi import HTTPException, BackgroundTasks
from tortoise import Tortoise

from .dto import *
from .model import CommentModel
from ..bug import BugsModel
from ..notification.dto import CreateNotificationDto
from ..notification.enum import EventNotificationEnum
from ..notification.service import NotificationService
import logging
logger = logging.getLogger(__name__)





class CommentBugService:
    @staticmethod
    async def create_history(bug_id: str, user: dict, text: str):
        try:
            return await CommentModel.create(
                create_date=datetime.datetime.now(),
                user_id=user.get('id'),
                bug_id=uuid.UUID(bug_id),
                text=text,
                view="history"
            )

        except Exception as e:
            logger.error(e, exc_info=True)
            pass

    @staticmethod
    async def create_comment(bug_id: str, data: CreateCommentDto, user: dict, background_tasks: BackgroundTasks):
        bug = await BugsModel.filter(id=bug_id).get_or_none()
        if not bug:
            raise HTTPException(status_code=404, detail="not found")

        temp = await CommentModel.create(
            create_date=datetime.datetime.now(),
            user_id=user.get('id'),
            bug_id=uuid.UUID(bug_id),
            text=data.text
        )

        try:
            if bug.create_user_id and str(bug.create_user_id) != str(user.get('id')):
                background_tasks.add_task(NotificationService.update_state_bug,
                                          CommentBugService.create_notification(bug, bug.__getattribute__('create_user_id'), data.text))

            if bug.assigner_id and str(bug.assigner_id) != str(user.get('id')):
                background_tasks.add_task(NotificationService.update_state_bug,
                                          CommentBugService.create_notification(bug, bug.__getattribute__('assigner_id'), data.text))
        except Exception as e:
            logger.error(e, exc_info=True)
            pass

        return await CommentBugService.get_comment_by_id(temp.id)

    @staticmethod
    def create_notification(bug: Any, user_id: str, comment_text: str):
        return CreateNotificationDto(
                    user=str(user_id),
                    data={
                                  "space_id": str(bug.__getattribute__("spaces_id")),
                                  "bug_id": str(bug.id),
                                  "short_name": str(bug.short_name),
                                  "changes": {
                                      "name": "comment",
                                      "from": "",
                                      "to": comment_text
                                  }
                    },
                    event=EventNotificationEnum.comment)
    @staticmethod
    async def get_comment(bug_id: str):
        conn = Tortoise.get_connection("default")
        sql = "SELECT commentmodel.id as id, commentmodel.create_date, commentmodel.text, commentmodel.bug_id, \
                   commentmodel.user_id, commentmodel.view, \
                    json_build_object('id', u.id, 'username', u.username, 'mail', u.mail, 'avatar_id', u.avatar_id, \
                    'avatar', json_build_object('id', f.id, 'filepath', f.filepath)) as create_user \
            FROM commentmodel \
                LEFT JOIN usermodel u on commentmodel.user_id = u.id \
                LEFT JOIN filemodel f on f.id = u.avatar_id \
            WHERE commentmodel.bug_id = $1 \
            ORDER BY commentmodel.create_date"

        temp = await conn.execute_query_dict(sql, [bug_id])
        for elem in temp:
            elem['create_user'] = json.loads(elem['create_user'])
        return temp

    @staticmethod
    async def update_comment(comment_id: str, data: UpdateCommentDto, user: dict):
        temp = await CommentModel.filter(id=comment_id).get_or_none()
        if not temp:
            raise HTTPException(status_code=404, detail="not found")

        if str(temp.__getattribute__('user_id')) != str(user.get('id')):
            raise HTTPException(status_code=403, detail="not have right")

        await CommentModel.filter(id=comment_id).update(text=data.text)

        return await CommentBugService.get_comment_by_id(comment_id)

    @staticmethod
    async def delete_comment(comment_id: str, user: dict):
        temp = await CommentModel.filter(id=comment_id).get_or_none()
        if not temp:
            raise HTTPException(status_code=404, detail="not found")
        if str(temp.user_id) != str(user.get('id')):
            raise HTTPException(status_code=403, detail="not have right")
        await temp.delete()

        return True

    @staticmethod
    async def get_comment_by_id(comment_id: str):
        conn = Tortoise.get_connection("default")
        sql = "SELECT commentmodel.id as id, commentmodel.create_date, commentmodel.text, commentmodel.bug_id, \
                   commentmodel.user_id, commentmodel.view, \
                    json_build_object('id', u.id, 'username', u.username, 'mail', u.mail, 'avatar_id', u.avatar_id, \
                    'avatar', json_build_object('id', f.id, 'filepath', f.filepath)) as create_user \
            FROM commentmodel \
                LEFT JOIN usermodel u on commentmodel.user_id = u.id \
                LEFT JOIN filemodel f on f.id = u.avatar_id \
            WHERE commentmodel.id = $1 \
            ORDER BY commentmodel.create_date"

        temp = (await conn.execute_query_dict(sql, [comment_id]))[0]
        temp['create_user'] = json.loads(temp['create_user'])

        return temp
