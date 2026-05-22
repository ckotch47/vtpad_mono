import uuid

from pydantic import BaseModel
from typing import Union


class CreatePadFolderDto(BaseModel):
    name: str | None = None
    main_id: str | None = None

