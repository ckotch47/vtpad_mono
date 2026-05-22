from datetime import datetime

from tortoise.models import Model
from tortoise import fields


class ToDoModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    create_date = fields.DatetimeField(null=False, default=datetime.now())
    title = fields.TextField(null=True)

    estimate_date = fields.DatetimeField(null=True, default=None)
