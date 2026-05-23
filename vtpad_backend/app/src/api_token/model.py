from tortoise.models import Model
from tortoise import fields


class ApiTokenModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    token_hash = fields.CharField(null=False, max_length=255, index=True)
    name = fields.TextField(null=False)
    scopes = fields.JSONField(null=True, default=list)

    last_used_at = fields.DatetimeField(null=True)
    expires_at = fields.DatetimeField(null=True)

    user = fields.ForeignKeyField('models.UserModel', related_name='api_tokens')
    created_at = fields.DatetimeField(null=False, auto_now_add=True)

    class Meta:
        table = "api_token"
