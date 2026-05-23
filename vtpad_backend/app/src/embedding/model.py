from tortoise.models import Model
from tortoise import fields


class EmbeddingModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    space_id = fields.UUIDField(index=True)
    source_type = fields.CharField(max_length=50, index=True)
    source_id = fields.UUIDField(index=True)
    source_field = fields.CharField(max_length=50, null=True)
    text_chunk = fields.TextField()
    embedding = fields.JSONField(null=True)  # Stored as list[float] for portability
    embedding_vector = fields.CharField(max_length=100, null=True)  # Placeholder for pgvector native
    created_at = fields.DatetimeField(null=True)

    class Meta:
        table = "embedding"
        indexes = [
            ("space_id", "source_type"),
            ("source_type", "source_id"),
        ]
