from typing import Union


class GetTestcaseItemDto:
    def __init__(
            self,
            with_all: Union[bool, None],
            sort: Union[str, None] = None,
            q: Union[str, None]=None
    ):
        if with_all is None:
            with_all = False
        self.with_all = with_all
        if q is None:
            q = None
        self.q = q
        if sort is None:
            sort = None
        self.sort = sort
