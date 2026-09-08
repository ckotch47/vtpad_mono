from pydantic import BaseModel
from typing import Optional, List


class TestRunCreateDto(BaseModel):
    name: str
    description: Optional[str] = None
    space_id: str
    suite_id: Optional[str] = None
    plan_id: Optional[str] = None
    milestone_id: Optional[str] = None
    environment_id: Optional[str] = None
    # Exactly one source is required: a suite, a plan, or an explicit non-empty
    # list.  The service validates this rather than falling back to all cases.
    testcase_ids: Optional[List[str]] = None
    source_hash: Optional[str] = None


class TestRunUpdateDto(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    milestone_id: Optional[str] = None
    environment_id: Optional[str] = None


class TestResultUpdateDto(BaseModel):
    status: str
    duration_seconds: Optional[int] = None
    comment: Optional[str] = None
    linked_bug_ids: Optional[List[str]] = None


class TestResultBulkUpdateDto(BaseModel):
    result_ids: List[str]
    status: str


