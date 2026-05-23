from tortoise.models import Model
from tortoise import fields


class EnvironmentModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=False)
    os = fields.TextField(null=True)
    browser = fields.TextField(null=True)
    url = fields.TextField(null=True)
    variables = fields.JSONField(null=True, default=dict)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='environments')
    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_environments', null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "environment"
