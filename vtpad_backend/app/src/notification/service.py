import json

from .model import NotificationModel
from .dto import *
from .enum import EventNotificationEnum
class NotificationService:
    @staticmethod
    async def get_notification(dto: GetNotificationDto, limit: int = 20, skip: int = 0):
        sql = f'SELECT * FROM notificationmodel '
        sql += f"WHERE user_id = '{dto.user_id}' "

        if dto.send is not None:
            sql += f'AND send = {dto.send} '

        if dto.read is not None:
            sql += f'AND read = {dto.read} '

        if dto.event is not None:
            sql += f'AND event = {dto.event} '

        sql += f'ORDER BY create_date DESC '

        sql += f"LIMIT {limit} "
        sql += f"OFFSET {skip}"

        return await NotificationModel.raw(sql)


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
        except:
            try:
                # todo add redis counter
                return await NotificationModel.create(
                    user_id=dto.user,
                    data=dto.data,
                    event=dto.event,
                    personal=dto.personal if dto.personal else True,
                    read=dto.read if dto.read else False
                )
            except:
                pass

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
            print(e, '3')
            pass

    @staticmethod
    async def send_notification(notification_id: str):
        try:
            await NotificationModel.filter(id=notification_id).update(send=True)
        except:
            pass

    @staticmethod
    async def get_count_unread_notification(user: dict):
        return await NotificationModel.filter(user_id=str(user.get('id')), read=False).count()

    @staticmethod
    async def read_all_notification(user: dict):
        return await NotificationModel.filter(user_id=str(user.get('id')), read=False).update(read=True)
