from pydantic import BaseModel


class CreateRunDto(BaseModel):
    name: str
