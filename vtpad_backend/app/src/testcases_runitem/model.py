from tortoise.models import Model
from tortoise import fields


class TestCaseRunItemModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    run_item = fields.ForeignKeyField('models.RunItemsModel', related_name='test_cases_rin_item_id', null=True)
    testcases = fields.ForeignKeyField('models.TestCasesModel', related_name='test_cases_run_id', null=True)
    state = fields.TextField(default=None, null=True)
