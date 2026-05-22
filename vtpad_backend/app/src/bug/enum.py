from enum import Enum


class StateBugEnum(str, Enum):
    open = 'OPEN'
    reopen = 'REOPEN'
    closed = "CLOSED"
    fixed = "FIXED"
    hold = "HOLD"
    ready = "READY"

    @staticmethod
    def get():
        enum = []
        for i in StateBugEnum:
            enum.append(i.title().upper())
        return enum
