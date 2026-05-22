from pydantic import BaseModel
from ..enum import *

class CreateChecklistDto(BaseModel):
    title: str
    text: str | None = None
    state: ChecklistStatusEnum | None = None
