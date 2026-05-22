from tortoise.models import Model
from tortoise import fields


class RunModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=True)
    date = fields.DatetimeField(null=False)
    pads = fields.ForeignKeyField('models.PadModel', related_name='pads')
