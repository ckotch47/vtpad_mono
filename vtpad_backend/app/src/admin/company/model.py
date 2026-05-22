from tortoise.models import Model
from tortoise import fields

from ..company.enum import ActiveEnum


class CompanyModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    create_date = fields.DatetimeField(null=False, auto_now_add=True)
    name = fields.TextField(null=False)
    status = fields.CharEnumField(ActiveEnum, max_length=64)
    max_person = fields.IntField(default=5)
