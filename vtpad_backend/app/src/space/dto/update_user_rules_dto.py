from typing import Union

from pydantic import BaseModel


class UpdateUserRulesForSpaceDto(BaseModel):
    readOnly: bool | None = None
    editPads: bool | None = None
    editItems: bool | None = None
    editRuns: bool | None = None
    editNotes: bool | None = None
    closeBugs: bool | None = None
    editTags: bool | None = None
    manageBugs: bool | None = None
    editTechDocs: bool | None = None
