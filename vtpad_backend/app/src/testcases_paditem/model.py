from tortoise.models import Model
from tortoise import fields


class TestCasePadItemModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    pad_item = fields.ForeignKeyField('models.ItemsModel', related_name='test_cases_pad_item_id', null=True)
    testcases = fields.ForeignKeyField('models.TestCasesModel', related_name='test_cases_pad_id', null=True)

