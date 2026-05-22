from typing import Union

from pydantic import BaseModel


class UpdateTestCaseDto(BaseModel):
    title: str | None = None
    text: str | None = None
    steps: str | None = None
    expected_results: str | None = None
    sort: str | None = None
    link: str | None = None
    pad_item_id: str | None = None
