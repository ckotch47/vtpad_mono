from tortoise.models import Model
from tortoise import fields


class BugTagsModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    tag = fields.ForeignKeyField('models.TagModel', related_name='TagSpace')
    bug = fields.ForeignKeyField('models.BugsModel', related_name='TagBug')
