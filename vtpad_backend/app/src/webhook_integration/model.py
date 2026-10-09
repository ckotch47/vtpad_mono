from tortoise import fields
from tortoise.models import Model


class WebhookIntegrationModel(Model):
    id = fields.UUIDField(pk=True)
    space_id = fields.UUIDField(index=True)
    name = fields.CharField(max_length=120)
    allowed_run_ids = fields.JSONField(default=list)
    credential_ciphertext = fields.TextField()
    credential_nonce = fields.CharField(max_length=32)
    key_version = fields.CharField(max_length=32)
    credential_hash_prefix = fields.CharField(max_length=16)
    active = fields.BooleanField(default=True)
    created_by_id = fields.UUIDField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    revoked_at = fields.DatetimeField(null=True)

    class Meta:
        table = 'webhook_integration'


class WebhookResultMappingModel(Model):
    id = fields.UUIDField(pk=True)
    integration = fields.ForeignKeyField(
        'models.WebhookIntegrationModel', related_name='result_mappings', on_delete=fields.CASCADE
    )
    external_id = fields.CharField(max_length=255)
    result = fields.ForeignKeyField(
        'models.TestResultModel', related_name='webhook_mappings', on_delete=fields.CASCADE
    )
    run_id = fields.UUIDField()

    class Meta:
        table = 'webhook_result_mapping'
        unique_together = (('integration', 'external_id'), ('integration', 'result_id'))


class WebhookRequestModel(Model):
    id = fields.UUIDField(pk=True)
    integration = fields.ForeignKeyField(
        'models.WebhookIntegrationModel', related_name='requests', on_delete=fields.CASCADE
    )
    request_id = fields.UUIDField()
    idempotency_key = fields.CharField(max_length=128)
    payload_hash = fields.CharField(max_length=64)
    nonce_hash = fields.CharField(max_length=64)
    status = fields.CharField(max_length=24)
    error_code = fields.CharField(max_length=64, null=True)
    result_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'webhook_request'
        unique_together = (('integration', 'idempotency_key'),)


class WebhookNonceModel(Model):
    id = fields.UUIDField(pk=True)
    integration = fields.ForeignKeyField(
        'models.WebhookIntegrationModel', related_name='nonces', on_delete=fields.CASCADE
    )
    nonce_hash = fields.CharField(max_length=64)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'webhook_nonce'
        unique_together = (('integration', 'nonce_hash'),)


class WebhookAuditEventModel(Model):
    id = fields.UUIDField(pk=True)
    integration = fields.ForeignKeyField(
        'models.WebhookIntegrationModel', related_name='audit_events', on_delete=fields.CASCADE
    )
    request_id = fields.UUIDField(unique=True)
    status = fields.CharField(max_length=24)
    error_code = fields.CharField(max_length=64, null=True)
    result_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'webhook_audit_event'
        indexes = (('integration', 'created_at'),)


class WebhookSecurityFailureBucketModel(Model):
    id = fields.UUIDField(pk=True)
    integration = fields.ForeignKeyField(
        'models.WebhookIntegrationModel', related_name='security_failure_buckets', on_delete=fields.CASCADE
    )
    minute_bucket = fields.DatetimeField()
    last_request_id = fields.UUIDField()
    error_code = fields.CharField(max_length=64)
    attempt_count = fields.IntField(default=1)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'webhook_security_failure_bucket'
        unique_together = (('integration', 'minute_bucket', 'error_code'),)


class WebhookResultProvenanceModel(Model):
    """One-to-one safe source metadata for a result last written by a webhook."""
    id = fields.UUIDField(pk=True)
    result = fields.OneToOneField(
        'models.TestResultModel', related_name='webhook_provenance', on_delete=fields.CASCADE
    )
    integration_id = fields.UUIDField()
    integration_name = fields.CharField(max_length=120)
    request_id = fields.UUIDField()
    updated_at = fields.DatetimeField()

    class Meta:
        table = 'webhook_result_provenance'
