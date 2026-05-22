from pydantic import BaseModel


class CreateSpaceDto(BaseModel):
    name: str