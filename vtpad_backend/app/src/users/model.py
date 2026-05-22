from tortoise.models import Model
from tortoise import fields


class UserModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    username = fields.TextField(null=True)
    mail = fields.CharField(40, null=False, unique=True)
    password = fields.TextField(null=False)
    avatar = fields.ForeignKeyField('models.FileModel', related_name='avatar', blank=True, null=True)

    class PydanticMeta:
        exclude = ("password",)
