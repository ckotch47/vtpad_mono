import uuid
from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel

from ..enum import StateBugEnum


class UpdateBugDto(BaseModel):
    title: str | None = None
    text: str | None = None
    steps: str | None = None
    additional_link: str | None = None

    assigner_id: Union[uuid.UUID, None] = None

    state: StateBugEnum | None = None

    estimate_date: Union[datetime, None] = None

    external_link: str | None = None


class UpdateBugDtoV2(BaseModel):
    title: str | None = None
    text: str | None = None
    steps: str | None = None
    additional_link: str | None = None

    assigner_id: str | None = None

    state: StateBugEnum | None = None

    estimate_date: str | None = None

    external_link: str | None = None

    tags: list[str] | None = None
