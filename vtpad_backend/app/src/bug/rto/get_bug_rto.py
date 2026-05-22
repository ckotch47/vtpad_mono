import datetime
import uuid
from typing import Any

from pydantic import BaseModel

from app.src.tag.rto import GetTagRto
from app.src.users.rto import AvatarRto


class ExternalLink(BaseModel):
    link: str
    task: str | None = None


class GetBugRto(BaseModel):
    id: str | uuid.UUID
    create_date: datetime.datetime
    update_date: datetime.datetime
    title: str
    text: str | None = None
    steps: str | None = None
    additional_link: str | None = None
    short_name: str | None = None
    create_user_id: str | uuid.UUID | None = None
    spaces_id: str | uuid.UUID | None = None
    assigner_id: str | uuid.UUID | None = None
    state: str | None = None
    estimate_date: datetime.datetime | None = None
    external_link: str | ExternalLink | None = None


class CreateUser(BaseModel):
    id: str | uuid.UUID
    mail: str
    username: str | None = None
    avatar: AvatarRto | Any


class Tag(BaseModel):
    id: str | uuid.UUID
    title: str | Any
    color: str | Any


class GetBugsWithFilterRto(GetBugRto):
    create_user: CreateUser | Any
    assigner_user: CreateUser | dict | Any
    tag: list[GetTagRto] | list | Any
