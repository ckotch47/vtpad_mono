import uuid

from fastapi import HTTPException


class GetBugDetailByShortNameDto:
    def __init__(
            self,
            space_id: uuid.UUID = '',
            short_name: str = ''
    ):
        if not space_id or not short_name:
            raise HTTPException(status_code=422, detail=f'not space_id')

        self.space_id = space_id
        self.short_name = short_name
