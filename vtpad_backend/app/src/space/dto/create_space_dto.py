from pydantic import BaseModel


from typing import Optional

class CreateSpaceDto(BaseModel):
    name: str
    short_name: Optional[str] = None