from typing import Union

from pydantic import BaseModel


class UpdateUserDto(BaseModel):
    username: str | None = None
    avatarId: str | None = None
