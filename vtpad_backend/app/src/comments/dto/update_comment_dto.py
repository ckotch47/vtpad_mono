from pydantic import BaseModel


class UpdateCommentDto(BaseModel):
    text: str
