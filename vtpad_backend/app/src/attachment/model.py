from tortoise.models import Model
from tortoise import fields


class AttachmentModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    entity_type = fields.CharField(null=False, max_length=50)  # e.g. "testcase", "testrun", "bug"
    entity_id = fields.UUIDField(null=False, index=True)

    file = fields.ForeignKeyField('models.FileModel', related_name='attachments', null=True)

    uploaded_by = fields.ForeignKeyField('models.UserModel', related_name='uploaded_attachments', null=True)
    uploaded_at = fields.DatetimeField(null=False, auto_now_add=True)

    class Meta:
        table = "attachment"
