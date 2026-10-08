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


class TestCasePriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TestCaseModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    title = fields.TextField(null=False)
    text = fields.TextField(null=True)
    steps = fields.TextField(null=True)
    expected_results = fields.TextField(null=True)
    preconditions = fields.TextField(null=True)
    postconditions = fields.TextField(null=True)
    estimated_duration_seconds = fields.IntField(null=True)
    priority = fields.CharEnumField(TestCasePriority, default=TestCasePriority.P2, max_length=2)

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
    estimated_duration_seconds = fields.IntField(null=True)
    # NULL on rows predating SU8 means the historical value is unknown.
    type = fields.CharEnumField(TestCaseType, null=True, max_length=20)
    priority = fields.CharField(null=True, max_length=2)
    tag_labels = fields.JSONField(null=True)

    testcase = fields.ForeignKeyField('models.TestCaseModel', related_name='versions')
    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_test_case_versions', null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)

    class Meta:
        table = "test_case_version"


class TestCaseTagModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    space = fields.ForeignKeyField('models.SpaceModel', related_name='test_case_tags', on_delete=fields.CASCADE)
    name = fields.CharField(max_length=255)
    normalized_name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "test_case_tag"
        unique_together = (("space", "normalized_name"),)


class TestCaseTagLinkModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    testcase = fields.ForeignKeyField('models.TestCaseModel', related_name='tag_links', on_delete=fields.CASCADE)
    tag = fields.ForeignKeyField('models.TestCaseTagModel', related_name='case_links', on_delete=fields.CASCADE)

    class Meta:
        table = "test_case_tag_link"
        unique_together = (("testcase", "tag"),)
