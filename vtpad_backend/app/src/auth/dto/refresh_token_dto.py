from pydantic import BaseModel


class RefreshTokenDto(BaseModel):
    refresh_token: str
