from typing import List

from pydantic import BaseModel


class TechDocTestCaseLinkDto(BaseModel):
    tech_doc_id: str
    testcase_id: str


class TechDocTestCasesReplaceDto(BaseModel):
    testcase_ids: List[str]
