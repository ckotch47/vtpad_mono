import uuid
from datetime import datetime, date
from typing import Union, List
from typing_extensions import Annotated

from fastapi import HTTPException
from fastapi.params import Query

from app.src.bug.enum import StateBugEnum


class GetBugsDto:
    def __init__(
            self,
            date_start: date = None,
            date_end: date = None,
            create_user: uuid.UUID = None,
            space_id: uuid.UUID = '',
            state: Union[List[StateBugEnum], None] = Query(default=None),

    ):
        if not space_id:
            raise HTTPException(status_code=422, detail=f'not space_id')
        self.date_start = date_start
        self.date_end = date_end
        self.create_user = create_user
        self.space_id = space_id
        if not date_start or not date_end or not create_user:
            raise HTTPException(status_code=422, detail=f'not date_start, date_end, create_user')
        if state is not None:
            self.state = state
        else:
            self.state = None

