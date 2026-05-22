from pydantic import BaseModel


class UpdateTagDto(BaseModel):
    title: str
    color: str
