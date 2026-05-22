from pydantic import BaseModel

class AddCompanyDto(BaseModel):
    name: str
    max_person: int


