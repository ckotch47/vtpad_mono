from enum import Enum

from tortoise.models import Model
from tortoise import fields


class TechDocType(str, Enum):
    api_doc = "api_doc"
    prd = "prd"
    manual = "manual"
    wiki = "wiki"
    migration = "migration"
    other = "other"


class TechDocModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    space_id = fields.UUIDField(index=True)
    title = fields.TextField(null=False)
    content = fields.TextField(null=True)
    source_url = fields.TextField(null=True)
    doc_type = fields.CharEnumField(TechDocType, default=TechDocType.other, max_length=20)
    version = fields.CharField(null=True, max_length=50)
    content_hash = fields.CharField(null=True, max_length=64)
    sort = fields.IntField(default=0)
    parent_id = fields.UUIDField(null=True, index=True)

    class Meta:
        table = "tech_doc"
