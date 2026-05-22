from tortoise.models import Model
from tortoise import fields


class FileModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    filepath = fields.CharField(null=True, max_length=255)
