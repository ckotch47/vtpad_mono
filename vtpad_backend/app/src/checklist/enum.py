from enum import Enum


class ChecklistStatusEnum(str, Enum):
    actual = 'ACTUAL'
    draft = 'DRAFT'
    deprecated = "DEPRECATED"


    @staticmethod
    def get():
        enum = []
        for i in ChecklistStatusEnum:
            enum.append(i.title().upper())
        return enum
