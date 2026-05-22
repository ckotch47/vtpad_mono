from pydantic import BaseModel


class AddTagToBugDto(BaseModel):
    tag_id: str

