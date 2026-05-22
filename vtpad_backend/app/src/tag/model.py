from datetime import datetime

from tortoise.models import Model
from tortoise import fields


class TagModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    create_date = fields.DatetimeField(null=False, auto_now_add=True)
    title = fields.TextField(null=False)
    color = fields.TextField(null=True)
    space = fields.ForeignKeyField('models.SpaceModel', related_name='spaceTag')
