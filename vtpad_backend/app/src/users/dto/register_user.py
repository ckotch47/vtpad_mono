from typing import Union

from pydantic import BaseModel


class RegisterUserDto(BaseModel):
    username: str | None = None
    mail: str
    password: str
