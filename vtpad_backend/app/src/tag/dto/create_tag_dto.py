from pydantic import BaseModel


class CreateTagDto(BaseModel):
    title: str
    color: str
