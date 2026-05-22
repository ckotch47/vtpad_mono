import uuid
from datetime import datetime, date
from typing import Union, List
from typing_extensions import Annotated

from fastapi import HTTPException
from fastapi.params import Query

from ..enum import StateBugEnum


class GetBugsDto:
    def __init__(
            self,
            create_date: Union[date, None] = None,
            create_date_end: date | None = None,

            create_user: Union[List[str], None] = Query(default=None),
            space_id: uuid.UUID = '',

            assigner_id: Union[List[str], None] = Query(default=None),

            state: Union[List[StateBugEnum], None] = Query(default=None),
            external_link: Union[list[str], None] = Query(default=None),

            estimate_date: Union[date, None] = None,
            estimate_date_end: date | None = None,

            not_assigner: Union[bool, None] = None,
            order_by: Union[str, None] = None,
            order_arrow: Union[str, None] = 'ASC',
            show_closed: Union[bool, None] = None,
            tag: Union[list[str], None] = Query(default=None),
            skip: int = 0,
            limit: int = 100
    ):
        if not space_id:
            raise HTTPException(status_code=422, detail=f'not space_id')
        self.create_date = create_date
        self.create_date_end = create_date_end

        self.create_user = create_user
        self.space_id = space_id
        self.assigner_id = assigner_id

        if state is not None:
            self.state = state
        else:
            self.state = None
        self.external_link = external_link

        self.estimate_date = estimate_date
        self.estimate_date_end = estimate_date_end

        self.skip = skip
        self.limit = limit
        self.not_assigner = bool(not_assigner)
        self.order_by = order_by
        self.order_arrow = order_arrow
        self.show_closed = show_closed
        self.tag = tag
