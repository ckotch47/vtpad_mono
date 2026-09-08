from tortoise import fields
from tortoise.models import Model


class TechDocTestCaseLinkModel(Model):
    """Explicit same-space M:N relation used by requirement coverage views."""

    id = fields.UUIDField(pk=True, index=True)
    space_id = fields.UUIDField(index=True)
    tech_doc = fields.ForeignKeyField('models.TechDocModel', related_name='testcase_links', on_delete=fields.CASCADE)
    testcase = fields.ForeignKeyField('models.TestCaseModel', related_name='techdoc_links', on_delete=fields.CASCADE)
    created_at = fields.DatetimeField(null=False, auto_now_add=True)

    class Meta:
        table = 'tech_doc_test_case_link'
        unique_together = (('tech_doc', 'testcase'),)
