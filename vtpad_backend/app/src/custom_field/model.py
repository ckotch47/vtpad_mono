import json
from enum import Enum

from tortoise.models import Model
from tortoise import fields
import logging
logger = logging.getLogger(__name__)


class SafeJSONField(fields.JSONField):
    """JSONField that correctly handles primitive strings."""

    def to_python_value(self, value):
        if value is None:
            return None
        if isinstance(value, (str, bytes)):
            try:
                return self.decoder(value)
            except Exception as e:
                logger.error('Unexpected error: %s', e, exc_info=True)
                # If it's a plain string (not JSON-encoded), return as-is
                return value.decode() if isinstance(value, bytes) else value
        return value

    def to_db_value(self, value, instance):
        if value is None:
            return None
        # Always serialize through encoder so primitives are valid JSON
        return self.encoder(value)


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
    value = SafeJSONField(null=True)  # stored as JSON (string, number, list, bool)

    field = fields.ForeignKeyField('models.CustomFieldModel', related_name='values')

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "custom_field_value"
