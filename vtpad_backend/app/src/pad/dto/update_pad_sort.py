from pydantic import BaseModel
from typing import Union


class UpdateSortPadDto(BaseModel):
    sortAfterId: str | None = None
    sortBeforeId: str | None = None
