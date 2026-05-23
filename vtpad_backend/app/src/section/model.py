from tortoise.models import Model
from tortoise import fields


class SectionModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)
    sort = fields.IntField(default=0)

    # tree structure
    parent = fields.ForeignKeyField('models.SectionModel', related_name='children', null=True, on_delete=fields.SET_NULL)

    suite = fields.ForeignKeyField('models.TestSuiteModel', related_name='sections')
    created_by = fields.ForeignKeyField('models.UserModel', related_name='created_sections', null=True)

    created_at = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        table = "section"
