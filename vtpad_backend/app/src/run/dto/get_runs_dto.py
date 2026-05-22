import uuid
from datetime import datetime, date
from typing import Union, List
from typing_extensions import Annotated

from fastapi import HTTPException
from fastapi.params import Query


class GetRunsDto:
    def __init__(
            self,
            pad_id: str,
            skip: int = 0,
            limit: int = 10
    ):
        if not pad_id:
            raise HTTPException(status_code=422, detail=f'not pad_id')
        self.pad_id = pad_id
        self.skip = skip
        self.limit = limit
