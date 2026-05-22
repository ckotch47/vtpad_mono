from tortoise.models import Model
from tortoise import fields


class PadFolderModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=True)
    spaces = fields.ForeignKeyField('models.SpaceModel', related_name='spaceFolder')
    main = fields.ForeignKeyField('models.PadFolderModel')
    sort = fields.IntField()

