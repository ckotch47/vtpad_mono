from tortoise.models import Model
from tortoise import fields
from ..company.enum import ActiveEnum
from ..roles_enum import RolesEnum


class UserCompanySettingsModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    status = fields.CharEnumField(ActiveEnum, max_length=64)
    role = fields.CharEnumField(RolesEnum, max_length=64,)

    user = fields.ForeignKeyField('models.UserModel')
    company = fields.ForeignKeyField('models.CompanyModel')
