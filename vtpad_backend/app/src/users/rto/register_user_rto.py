from pydantic import BaseModel


class RegisterUserRto(BaseModel):
    access_token: str
    refresh_token: str
