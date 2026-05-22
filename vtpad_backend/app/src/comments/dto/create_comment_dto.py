from typing import Union

from pydantic import BaseModel


class CreateCommentDto(BaseModel):
    text: Union[str, None]
