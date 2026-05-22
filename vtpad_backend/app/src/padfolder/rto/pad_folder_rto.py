import uuid

from pydantic import BaseModel


class PadFolderRto(BaseModel):
    id: uuid.UUID | str
    name: str | None = None
    spaces_id: uuid.UUID | str
    main_id: uuid.UUID | str | None = None
    sort: int
