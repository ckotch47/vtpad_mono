from datetime import datetime

from tortoise.models import Model
from tortoise import fields


class NotesModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    create_date = fields.DatetimeField(null=False, auto_now_add=True)
    title = fields.TextField(null=True)
    text = fields.TextField(null=True)
    createUser = fields.ForeignKeyField('models.UserModel', related_name='user')
    spaces = fields.ForeignKeyField('models.SpaceModel', related_name='spaces')
