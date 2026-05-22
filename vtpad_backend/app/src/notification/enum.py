from enum import Enum

class EventNotificationEnum(str, Enum):
    create = 'CREATE'
    assign = 'ASSIGN'
    update = 'UPDATE'
    comment = 'COMMENT'
