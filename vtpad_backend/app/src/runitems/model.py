from tortoise.models import Model
from tortoise import fields, Tortoise


class RunItemsModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    itemId = fields.UUIDField(null=True, index=True)
    state = fields.TextField(default=None, null=True)
    run = fields.ForeignKeyField('models.RunModel', related_name='run')



