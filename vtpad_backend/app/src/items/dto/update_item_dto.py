from typing import Union

from pydantic import BaseModel


class UpdateItemDto(BaseModel):
    text: str | None = None
