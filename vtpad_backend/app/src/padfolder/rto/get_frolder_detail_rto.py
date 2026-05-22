import uuid
from typing import Any

from pydantic import BaseModel

from app.src.pad.rto import PadRto
from app.src.padfolder.rto import PadFolderRto


class GetFolderDetailRto(BaseModel):
    id: uuid.UUID | str
    name: str | None = None
    sort: int
    spaces: uuid.UUID | str | None = None
    main_id: uuid.UUID | str | None = None
    pad: list[PadRto]
    folder: list[PadFolderRto] | Any
