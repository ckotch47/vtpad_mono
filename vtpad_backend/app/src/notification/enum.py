from enum import Enum

class EventNotificationEnum(str, Enum):
    create = 'CREATE'
    assign = 'ASSIGN'
    update = 'UPDATE'
    comment = 'COMMENT'
    run_completed = 'RUN_COMPLETED'
