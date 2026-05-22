from pydantic import BaseModel


class ResetPasswordRto(BaseModel):
    password: str
