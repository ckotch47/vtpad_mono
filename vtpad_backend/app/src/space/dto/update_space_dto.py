from typing import Union

from pydantic import BaseModel


class UpdateSpaceDto(BaseModel):
    name: str
    short_name: str | None = None

