import uuid


from app.src.spacesuser.model import SpacesUserRole
from app.src.users.rto import UserRto


class GetUserForSpaceRto(UserRto):
    spaceId: str | uuid.UUID
    role: SpacesUserRole
    right: object | None = None
