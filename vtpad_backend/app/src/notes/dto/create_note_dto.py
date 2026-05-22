from pydantic import BaseModel


class CreateNoteDto(BaseModel):
    title: str
    text: str

