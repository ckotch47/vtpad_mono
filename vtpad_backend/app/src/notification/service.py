import json

from .model import NotificationModel
from .dto import *
from .enum import EventNotificationEnum
import logging
logger = logging.getLogger(__name__)
class NotificationService:
    @staticmethod
    async def get_notification(dto: GetNotificationDto, limit: int = 20, skip: int = 0):
        query = NotificationModel.filter(user_id=dto.user_id)

        if dto.send is not None:
            query = query.filter(send=dto.send)

        if dto.read is not None:
            query = query.filter(read=dto.read)

        if dto.event is not None:
            query = query.filter(event=dto.event)

        return await query.order_by('-create_date').offset(skip).limit(limit)


    @staticmethod
    async def add_notification_assign(dto: CreateNotificationDto):
        try:
            temp = await NotificationModel.filter(
                user_id=dto.user,
                data=dto.data,
                event=dto.event,
                personal=dto.personal if dto.personal else True,
                read=dto.read if dto.read else False
            ).get()
            if temp:
                return None
        except Exception:
            # Expected when notification does not exist yet
            try:
                # todo add redis counter
                return await NotificationModel.create(
                    user_id=dto.user,
                    data=dto.data,
                    event=dto.event,
                    personal=dto.personal if dto.personal else True,
                    read=dto.read if dto.read else False
                )
            except Exception as e:
                logger.error('Failed to create notification: %s', e, exc_info=True)

    @staticmethod
    async def read_notification(notifi_id: str):
        tmp = await NotificationModel.filter(id=notifi_id).get_or_none()
        if not tmp:
            return False
        tmp.read = True

        return await tmp.save()



    @staticmethod
    async def update_state_bug(dto: CreateNotificationDto):
        try:
            return await NotificationModel.create(
                user_id=dto.user,
                data=json.dumps(dto.data),
                event=dto.event,
                personal=dto.personal if dto.personal else True,
                read=dto.read if dto.read else False
            )
        except Exception as e:
            logger.error(e, exc_info=True)
            pass

    @staticmethod
    async def send_notification(notification_id: str):
        try:
            await NotificationModel.filter(id=notification_id).update(send=True)
        except Exception as e:
            logger.error('Failed to create notification: %s', e, exc_info=True)

    @staticmethod
    async def get_count_unread_notification(user: dict):
        return await NotificationModel.filter(user_id=str(user.get('id')), read=False).count()

    @staticmethod
    async def read_all_notification(user: dict):
        return await NotificationModel.filter(user_id=str(user.get('id')), read=False).update(read=True)
