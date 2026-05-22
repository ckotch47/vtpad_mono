from datetime import datetime, date
from typing import Union
from fastapi import HTTPException
from ..enum import EventNotificationEnum

class GetNotificationDto:
    def __init__(
            self,
            create_date: Union[date, None] = None,
            user_id: str = '-1',
            event: Union[EventNotificationEnum, None] = None,
            read: Union[bool, None] = None,
            send: Union[bool, None] = None,
            order: Union[str, None] = 'ASC',



    ):
        if user_id == '-1':
            raise HTTPException(status_code=422, detail=f'not user_id')
        self.user_id = user_id
        self.create_date = create_date
        self.event = event
        self.read = read
        self.order = order
        self.send = send

