from tortoise.models import Model
from tortoise import fields


class SpaceModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=True)
    sort = fields.IntField()
    short_name = fields.TextField(null=True)
    company = fields.ForeignKeyField('models.CompanyModel', related_name='spaceCompany')
