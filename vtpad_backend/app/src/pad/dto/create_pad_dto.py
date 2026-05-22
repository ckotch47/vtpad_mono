from pydantic import BaseModel
from typing import Union


class CreatePadDto(BaseModel):
    name: str
    folder_id: str | None = None
