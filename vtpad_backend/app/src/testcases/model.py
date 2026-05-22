from tortoise.models import Model
from tortoise import fields


class TestCasesModel(Model):
    id = fields.UUIDField(pk=True, index=True)

    create_date = fields.DatetimeField(null=False, auto_now_add=True)
    update_date = fields.DatetimeField(null=False, auto_now=True)

    title = fields.TextField(null=False)
    text = fields.TextField(null=True)
    steps = fields.TextField(null=True)
    expected_results = fields.TextField(null=True)

    sort = fields.IntField(null=True)

    short_name = fields.TextField(null=True)

    link = fields.TextField(null=True)
    space = fields.ForeignKeyField('models.SpaceModel', related_name='testcase_space')
