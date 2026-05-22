from pydantic import BaseModel


class GetStateEnumRto(BaseModel):
    state: list[str]
