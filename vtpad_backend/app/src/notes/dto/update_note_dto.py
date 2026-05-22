from typing import Union

from pydantic import BaseModel


class UpdateNoteDto(BaseModel):
    title: Union[str, None]
    text: Union[str, None]

