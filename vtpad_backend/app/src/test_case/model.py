from enum import Enum

from tortoise.models import Model
from tortoise import fields


class TestCaseType(str, Enum):
    manual = "manual"
    checklist = "checklist"
    automated = "automated"


class TestCaseStatus(str, Enum):
    draft = "draft"
    active = "active"
    deprecated = "deprecated"


class TestCaseModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    title = fields.TextField(null=False)
    text = fields.TextField(null=True)
    steps = fields.TextField(null=True)
    expected_results = fields.TextField(null=True)
    preconditions = fields.TextField(null=True)
    postconditions = fields.TextField(null=True)

    sort = fields.IntField(default=0)
    short_name = fields.CharField(null=True, max_length=255)
    link = fields.TextField(null=True)

    type = fields.CharEnumField(TestCaseType, default=TestCaseType.manual, max_length=20)
    status = fields.CharEnumField(TestCaseStatus, default=TestCaseStatus.draft, max_length=20)
    external_id = fields.CharField(null=True, max_length=255)  # for automated tests (e.g. pytest id)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='test_cases')
    suite = fields.ForeignKeyField('models.TestSuiteModel', related_name='test_cases', null=True, on_delete=fields.SET_NULL)
    section = fields.ForeignKeyField('models.SectionModel', related_name='test_cases', null=True, on_delete=fields.SET_NULL)
    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_test_cases', null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "test_case"


class TestCaseVersionModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    version_number = fields.IntField(default=1)

    title = fields.TextField(null=False)
    text = fields.TextField(null=True)
    steps = fields.TextField(null=True)
    expected_results = fields.TextField(null=True)
    preconditions = fields.TextField(null=True)
    postconditions = fields.TextField(null=True)

    testcase = fields.ForeignKeyField('models.TestCaseModel', related_name='versions')
    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_test_case_versions', null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)

    class Meta:
        table = "test_case_version"
