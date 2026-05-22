from pydantic import BaseModel


class RefreshTokenRto(BaseModel):
    access_token: str
    refresh_token: str
