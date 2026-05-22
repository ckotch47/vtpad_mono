from datetime import datetime


from tortoise.models import Model
from tortoise import fields

from .enum import StateBugEnum


class BugsModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    create_date = fields.DatetimeField(null=False, auto_now_add=True)
    update_date = fields.DatetimeField(null=False, auto_now=True)
    title = fields.TextField(null=False)
    text = fields.TextField(null=True)
    steps = fields.TextField(null=True)
    additional_link = fields.TextField(null=True)

    short_name = fields.TextField(null=True)

    create_user = fields.relational.ForeignKeyField('models.UserModel', related_name='bugCreateUser')
    spaces = fields.ForeignKeyField('models.SpaceModel', related_name='bugSpace')

    assigner = fields.ForeignKeyField('models.UserModel', related_name='bugAssignerUser', blank=True, null=True)

    state = fields.CharEnumField(StateBugEnum, f'enum {StateBugEnum}', 40)

    estimate_date = fields.DatetimeField(null=True, default=None)

    external_link = fields.TextField(null=True)
