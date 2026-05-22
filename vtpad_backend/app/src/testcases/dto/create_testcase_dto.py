from typing import Union

from pydantic import BaseModel


class CreateTestCaseDto(BaseModel):
    title: str | None = None
    text: str | None = None
    steps: str | None = None
    expected_results: str | None = None
    space_id: str
    link: str | None = None
