from tortoise import fields
from tortoise.models import Model


class TestCaseTemplateModel(Model):
    id = fields.UUIDField(pk=True)
    space = fields.ForeignKeyField(
        'models.SpaceModel', related_name='case_templates', on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=120)
    normalized_name = fields.TextField()
    description = fields.TextField(null=True)
    created_by_id = fields.UUIDField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'test_case_template'
        unique_together = (('space', 'normalized_name'),)


class TestCaseTemplateVersionModel(Model):
    id = fields.UUIDField(pk=True)
    template = fields.ForeignKeyField(
        'models.TestCaseTemplateModel', related_name='versions', on_delete=fields.CASCADE
    )
    version_number = fields.IntField()
    content = fields.JSONField()
    created_by_id = fields.UUIDField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'test_case_template_version'
        unique_together = (('template', 'version_number'),)
