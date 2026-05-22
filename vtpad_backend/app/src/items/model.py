from tortoise.models import Model
from tortoise import fields


class ItemsModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    text = fields.TextField(null=True)
    sort = fields.IntField()
    mainId = fields.UUIDField(null=True, default=None)
    pad = fields.ForeignKeyField('models.PadModel', related_name='pad')
    description = fields.TextField(null=True)