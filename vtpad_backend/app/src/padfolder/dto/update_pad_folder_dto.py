from pydantic import BaseModel
from typing import Union


class UpdatePadFolderDto(BaseModel):
    name: str | None = None

