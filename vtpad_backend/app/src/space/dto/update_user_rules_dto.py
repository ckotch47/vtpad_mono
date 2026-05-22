from typing import Union

from pydantic import BaseModel


class UpdateUserRulesForSpaceDto(BaseModel):
    editPads: bool | None = None
    editItems: bool | None = None
    editRuns: bool | None = None
    editNotes: bool | None = None
    closeBugs: bool | None = None
    editTags: bool | None = None
