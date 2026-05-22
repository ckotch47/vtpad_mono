import uuid

from pydantic import BaseModel


class GetTestCaseByShortName(BaseModel):
    id: uuid.UUID | str