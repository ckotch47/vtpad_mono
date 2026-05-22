from enum import Enum

from pydantic import BaseModel


class State(str, Enum):
    PASS = 'pass'
    FAIL = 'fail'


class UpdateTestcaseRunItemDto(BaseModel):
    state: State = None
