from typing import Union


class GetTestcaseDto:
    def __init__(
            self,
            q: Union[str, None],
            sort: Union[str, None] = None,
            limit: int | None = None,
            offset: int | None = None
    ):
        if q is None:
            self.q = None
        self.q = q
        self.sort = sort

        self.limit = limit if limit else 100
        self.offset = offset if offset else 0
