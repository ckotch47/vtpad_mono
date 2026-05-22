from pydantic import BaseModel


class AuthUserDto(BaseModel):
    mail: str
    password: str
