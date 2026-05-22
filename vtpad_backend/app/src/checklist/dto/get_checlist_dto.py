from fastapi import HTTPException


class GetChecklistDto:
    def __init__(
            self,
            q: str | None = None,
            sort: str | None = None,
            limit: int | None = None,
            offset: int | None = None
    ):
        self.q = q if q else ''
        if sort not in ['ASC', 'DESC', None]:
            raise HTTPException(status_code=422, detail="sort invalid")
        self.sort = sort if sort else 'DESC'
        self.limit = limit if limit else 100
        self.offset = offset if offset else 0
