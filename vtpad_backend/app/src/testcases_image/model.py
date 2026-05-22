from tortoise.models import Model
from tortoise import fields


class TestCaseImageModel(Model):
    id = fields.UUIDField(pk=True, index=True)

    testcase = fields.ForeignKeyField('models.TestCasesModel', related_name='testcase_image_testcase')
    file = fields.ForeignKeyField('models.FileModel', related_name='testcase_image_file')
