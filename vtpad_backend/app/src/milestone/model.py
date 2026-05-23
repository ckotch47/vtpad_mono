from enum import Enum

from tortoise.models import Model
from tortoise import fields


class MilestoneStatus(str, Enum):
    active = "active"
    closed = "closed"


class MilestoneModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    title = fields.TextField(null=False)
    description = fields.TextField(null=True)
    start_date = fields.DateField(null=True)
    end_date = fields.DateField(null=True)

    status = fields.CharEnumField(MilestoneStatus, default=MilestoneStatus.active, max_length=20)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='milestones')
    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_milestones', null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "milestone"
