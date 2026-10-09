from tortoise.models import Model
from tortoise import fields
from .enum import EventNotificationEnum


class NotificationModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    create_date = fields.DatetimeField(null=False, auto_now_add=True)
    user = fields.ForeignKeyField('models.UserModel',  related_name='Notification_userId')
    run = fields.ForeignKeyField(
        'models.TestRunModel', related_name='completion_notifications',
        null=True, on_delete=fields.CASCADE,
    )
    data = fields.JSONField(null=True)
    event = fields.CharEnumField(EventNotificationEnum, f'enum {EventNotificationEnum}', 40)
    personal = fields.BooleanField(default=True)
    read = fields.BooleanField(default=False)
    send = fields.BooleanField(default=False)

    class Meta:
        table = "notificationmodel"
