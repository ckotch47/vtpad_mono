from tortoise.models import Model
from tortoise import fields
from enum import Enum


class SpacesUserRole(str, Enum):
    owner = 'OWNER'
    collaborator = 'COLLABORATOR'


class SpacesUserModel(Model):
    id = fields.UUIDField(pk=True, index=True)
    userId = fields.UUIDField(index=True, null=True)
    spaceId = fields.UUIDField(index=True, null=True)
    role = fields.CharEnumField(SpacesUserRole, 'owner or collaborator', 40)
    right = fields.JSONField(null=True, default={})
