from tortoise.models import Model
from tortoise import fields


class TestPlanModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)

    # Filters stored as JSONB for flexibility
    # Example: {"types": ["manual"], "sections": ["uuid"], "statuses": ["active"], "tags": ["uuid"]}
    filters = fields.JSONField(null=True, default=dict)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='test_plans')
    suite = fields.ForeignKeyField('models.TestSuiteModel', related_name='test_plans', null=True, on_delete=fields.SET_NULL)

    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_test_plans', null=True)
    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "test_plan"
