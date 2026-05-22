from enum import Enum

from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class ViewCommentEnum(str, Enum):
    comment = "comment"
    history = "history"


class CommentModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    create_date = fields.DatetimeField(null=False, auto_now=True)
    update_date = fields.DatetimeField(null=False, auto_now=True)
    text = fields.TextField(null=True)

    view = fields.TextField(null=True, default="comment")

    user = fields.ForeignKeyField('models.UserModel', related_name='commentCreateUser')

    bug = fields.ForeignKeyField('models.BugsModel', related_name='commentBug')
