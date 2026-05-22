from pydantic import BaseModel


class AddImageTestcaseDto(BaseModel):
    image_id: str
