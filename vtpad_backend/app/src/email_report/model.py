import uuid

from tortoise import fields
from tortoise.models import Model


class EmailReportSnapshotModel(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, index=True)
    space_id = fields.UUIDField(index=True)
    sender_user_id = fields.UUIDField(index=True)
    payload = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField(index=True)

    class Meta:
        table = 'email_report_snapshot'


class EmailReportDeliveryModel(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4, index=True)
    space_id = fields.UUIDField(index=True)
    sender_user_id = fields.UUIDField(index=True)
    snapshot_id = fields.UUIDField(index=True)
    idempotency_key = fields.UUIDField()
    request_digest = fields.CharField(max_length=64)
    recipient_user_id = fields.UUIDField(index=True)
    status = fields.CharField(max_length=16, default='pending')
    error_code = fields.CharField(max_length=32, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'email_report_delivery'
