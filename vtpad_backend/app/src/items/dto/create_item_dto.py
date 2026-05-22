from typing import Union

from pydantic import BaseModel


class CreateItemDto(BaseModel):
    text: str | None = None
    mainId: str | None = None
