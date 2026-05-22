from typing import Any

from pydantic import BaseModel

from app.src.space.rto import GetUserForSpaceRto
from app.src.tag.rto import GetTagRto


class GetFiltersRto(BaseModel):
    create_date: bool
    create_date_end: bool
    estimate_date: bool
    estimate_date_end: bool
    state: list[str]
    user: list[GetUserForSpaceRto]
    order_by: list[str]
    tag: list[GetTagRto] | Any
    external_link: list[str] | Any
