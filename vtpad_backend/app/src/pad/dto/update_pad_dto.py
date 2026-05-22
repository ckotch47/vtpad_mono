from pydantic import BaseModel
from typing import Union


class UpdatePadDto(BaseModel):
    name: str | None = None
    folder_id: str | None = None

