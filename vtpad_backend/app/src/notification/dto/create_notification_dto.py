from pydantic import BaseModel
from typing import Union, Any
from ..enum import EventNotificationEnum

class CreateNotificationDto(BaseModel):
    user: str
    data: dict | None | Any = None
    event: EventNotificationEnum
    personal: bool | None = None
    read: bool | None = None
