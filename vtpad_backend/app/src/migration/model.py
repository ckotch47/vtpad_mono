from tortoise.models import Model
from tortoise import fields


class MigrationModel(Model):
    id = fields.UUIDField(pk=True)
    create_date = fields.DatetimeField(auto_now_add=True)
    name = fields.CharField(max_length=255, index=True)

    class Meta:
        table = "migrationmodel"
