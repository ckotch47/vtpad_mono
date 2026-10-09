import uuid

from tortoise import fields
from tortoise.models import Model


class PublicRunLinkModel(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    run = fields.ForeignKeyField(
        'models.TestRunModel', related_name='public_links', on_delete=fields.CASCADE
    )
    token_digest = fields.CharField(max_length=64, unique=True)
    token_version = fields.CharField(max_length=16)
    key_version = fields.CharField(max_length=32)
    created_by = fields.ForeignKeyField(
        'models.UserModel', related_name='created_public_run_links', on_delete=fields.CASCADE
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()
    revoked_at = fields.DatetimeField(null=True)

    class Meta:
        table = 'public_run_link'
