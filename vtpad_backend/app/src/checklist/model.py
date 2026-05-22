from tortoise.models import Model
from tortoise import fields

from .enum import ChecklistStatusEnum


class ChecklistModel(Model):
    id = fields.UUIDField(pk=True, index=True)

    create_date = fields.DatetimeField(null=False, auto_now_add=True)
    update_date = fields.DatetimeField(null=False, auto_now=True)

    title = fields.TextField(null=False)
    text = fields.TextField(null=True)

    sort = fields.IntField(null=True)

    short_name = fields.TextField(null=True)

    state =fields.CharEnumField(ChecklistStatusEnum, f'enum {ChecklistStatusEnum}', 40)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='checklist_space')