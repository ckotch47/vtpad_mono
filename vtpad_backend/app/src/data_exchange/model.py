from tortoise import fields
from tortoise.models import Model


class ImportReceiptModel(Model):
    """Durable idempotency record for an import, including post-commit work."""

    id = fields.UUIDField(pk=True, index=True)
    idempotency_key = fields.CharField(max_length=200)
    content_hash = fields.CharField(max_length=64)
    actor_id = fields.UUIDField(index=True)
    space = fields.ForeignKeyField(
        "models.SpaceModel", related_name="data_exchange_import_receipts", on_delete=fields.CASCADE
    )
    response = fields.JSONField()
    created_case_ids = fields.JSONField(default=list)
    embeddings_pending = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "data_exchange_import_receipt"
