from tortoise.models import Model
from tortoise import fields


class PadModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=True)
    spaces = fields.ForeignKeyField('models.SpaceModel', related_name='space')
    sort = fields.IntField()
    folder = fields.ForeignKeyField('models.PadFolderModel', related_name='folder', null=True)
