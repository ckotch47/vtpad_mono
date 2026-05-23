from enum import Enum

from tortoise.models import Model
from tortoise import fields


class TestSuiteStatus(str, Enum):
    active = "active"
    archived = "archived"


class TestSuiteModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)
    sort = fields.IntField(default=0)
    status = fields.CharEnumField(TestSuiteStatus, default=TestSuiteStatus.active, max_length=20)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='test_suites')
    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_test_suites', null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "test_suite"
