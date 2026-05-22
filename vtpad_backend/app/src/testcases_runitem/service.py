from .model import TestCaseRunItemModel
from .dto import *


class TestcasesRunitemService:
    def __init__(self):
        self.model = TestCaseRunItemModel()

    async def update_test_case_runitem(self, ids: str, state: State):
        return bool(await self.model.filter(id=ids).update(state=state))
