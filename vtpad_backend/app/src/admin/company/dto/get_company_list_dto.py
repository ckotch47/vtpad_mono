class GetCompanyListDto:
    def __init__(
            self,
            q: str | None,
            limit: int = 0,
            offset: int = 100
                 ):
        if q is None:
            self.q = ''
        else:
            self.q = q

        self.limit = limit
        self.offset = offset
