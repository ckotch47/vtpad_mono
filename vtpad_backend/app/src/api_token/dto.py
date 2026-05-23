from pydantic import BaseModel
from typing import Optional, List


class ApiTokenCreateDto(BaseModel):
    name: str
    scopes: Optional[List[str]] = None
    expires_at: Optional[str] = None  # ISO datetime string


class ApiTokenRevokeDto(BaseModel):
    token_id: str
