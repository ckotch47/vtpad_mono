import uuid
from datetime import datetime
from typing import Union

from pydantic import BaseModel

from ..enum import StateBugEnum


class CreateBugDto(BaseModel):
    title: str | None = None
    text: str | None = None
    steps: str | None = None
    additional_link: str | None = None

    space_id: uuid.UUID
    assigner: str | None = None

    state: StateBugEnum

    estimate_date: str | None = None

    external_link: str | None = None