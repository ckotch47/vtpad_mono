from pydantic import BaseModel


class AddUserSpaceDto(BaseModel):
    mail: str
