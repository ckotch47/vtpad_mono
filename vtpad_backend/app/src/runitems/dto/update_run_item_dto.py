from enum import Enum

from pydantic import BaseModel


class State(str, Enum):
    PASS = 'pass'
    FAIL = 'fail'
    SKIP = 'skip'


class UpdateRunItemDto(BaseModel):
    state: State = None
