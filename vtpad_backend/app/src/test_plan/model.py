from tortoise.models import Model
from tortoise import fields


class TestPlanModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)

    case_ids = fields.JSONField(null=True, default=list)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='test_plans')

    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_test_plans', null=True)
    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "test_plan"
