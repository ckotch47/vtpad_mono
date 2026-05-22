from typing import Union

from pydantic import BaseModel


class UpdateSortItemDto(BaseModel):
    sortAfterId: str | None = None
    sortBeforeId: str | None = None