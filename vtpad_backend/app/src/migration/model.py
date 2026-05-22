from tortoise.models import Model
from tortoise import fields


class MigrationModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    create_date = fields.DatetimeField(null=False, auto_now_add=True)
    name = fields.TextField()
