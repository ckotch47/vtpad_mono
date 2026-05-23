from pydantic import BaseModel
from typing import Optional, List


class TestRunCreateDto(BaseModel):
    name: str
    description: Optional[str] = None
    space_id: str
    suite_id: Optional[str] = None
    milestone_id: Optional[str] = None
    environment_id: Optional[str] = None
    testcase_ids: Optional[List[str]] = None  # if None - all testcases from suite


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
