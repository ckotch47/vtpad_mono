from enum import Enum

from tortoise.models import Model
from tortoise import fields


class TestRunStatus(str, Enum):
    draft = "draft"
    active = "active"
    completed = "completed"


class TestResultStatus(str, Enum):
    not_run = "not_run"
    passed = "passed"
    failed = "failed"
    blocked = "blocked"
    skipped = "skipped"


class TestRunModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)

    status = fields.CharEnumField(TestRunStatus, default=TestRunStatus.draft, max_length=20)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='test_runs')
    suite = fields.ForeignKeyField('models.TestSuiteModel', related_name='test_runs', null=True, on_delete=fields.SET_NULL)
    plan = fields.ForeignKeyField('models.TestPlanModel', related_name='test_runs', null=True, on_delete=fields.SET_NULL)
    milestone = fields.ForeignKeyField('models.MilestoneModel', related_name='test_runs', null=True, on_delete=fields.SET_NULL)
    environment = fields.ForeignKeyField('models.EnvironmentModel', related_name='test_runs', null=True, on_delete=fields.SET_NULL)

    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_test_runs', null=True)
    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "test_run"


class TestResultModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    status = fields.CharEnumField(TestResultStatus, default=TestResultStatus.not_run, max_length=20)
    duration_seconds = fields.IntField(null=True)
    comment = fields.TextField(null=True)
    linked_bug_ids = fields.JSONField(null=True, default=list)

    run = fields.ForeignKeyField('models.TestRunModel', related_name='results')
    testcase = fields.ForeignKeyField('models.TestCaseModel', related_name='test_results')
    testcase_version = fields.ForeignKeyField('models.TestCaseVersionModel', related_name='version_results', null=True, on_delete=fields.SET_NULL)

    executed_by = fields.ForeignKeyField('models.UserModel', related_name='executed_test_results', null=True)
    executed_at = fields.DatetimeField(null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "test_result"


class TestStepResultModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    step_index = fields.IntField(default=0)
    step_text = fields.TextField(null=True)
    status = fields.CharEnumField(TestResultStatus, default=TestResultStatus.not_run, max_length=20)
    comment = fields.TextField(null=True)
    screenshot_url = fields.TextField(null=True)

    result = fields.ForeignKeyField('models.TestResultModel', related_name='step_results')

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "test_step_result"
