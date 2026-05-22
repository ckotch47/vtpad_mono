from tortoise import Model, fields


class ItemChecklistTestcaseModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    item = fields.ForeignKeyField('models.ItemsModel', related_name='items__id', null=True)
    checklist = fields.ForeignKeyField('models.ChecklistModel', related_name='items_checklist_id', null=True)
    testcase = fields.ForeignKeyField('models.TestCasesModel', related_name='items_testcase_id', null=True)

