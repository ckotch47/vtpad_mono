from enum import Enum

from tortoise.models import Model
from tortoise import fields


class CustomFieldEntityType(str, Enum):
    testcase = "testcase"
    testrun = "testrun"


class CustomFieldType(str, Enum):
    text = "text"
    select = "select"
    multiselect = "multiselect"
    number = "number"
    date = "date"
    checkbox = "checkbox"


class CustomFieldModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=False)
    field_type = fields.CharEnumField(CustomFieldType, max_length=20)
    entity_type = fields.CharEnumField(CustomFieldEntityType, max_length=20)
    options = fields.JSONField(null=True, default=list)  # list of strings for select/multiselect
    sort = fields.IntField(default=0)

    space = fields.ForeignKeyField('models.SpaceModel', related_name='custom_fields')
    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_custom_fields', null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "custom_field"


class CustomFieldValueModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    entity_id = fields.UUIDField(null=False, index=True)  # UUID of testcase or testrun
    value = fields.JSONField(null=True)  # stored as JSON (string, number, list, bool)

    field = fields.ForeignKeyField('models.CustomFieldModel', related_name='values')

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "custom_field_value"
