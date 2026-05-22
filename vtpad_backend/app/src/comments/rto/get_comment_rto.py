import datetime
import uuid

from pydantic import BaseModel

from app.src.users.rto import UserRto


class GetCommentRto(BaseModel):
    id: uuid.UUID | str
    create_date: datetime.datetime
    text: str
    bug_id: uuid.UUID | str
    user_id: uuid.UUID | str
    view: str
    create_user: UserRto