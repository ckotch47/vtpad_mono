import tortoise.exceptions
from fastapi import HTTPException

from .model import TestCasePadItemModel
from .dto import *


class TestcasesPaditemService:
    def __init__(self):
        self.model = TestCasePadItemModel()

    async def update_test_case_paditem(self, item_id: str, testcase_id: str):
        try:
            temp = await self.model.filter(pad_item_id=item_id, testcases_id=testcase_id).get()
            if temp:
                raise HTTPException(status_code=400, detail=f'duplicate')
        except HTTPException as e:
            print(e.status_code)
            if e.status_code == 400:
                raise HTTPException(status_code=400, detail=f'duplicate')
        except tortoise.exceptions.DoesNotExist as e:

            return bool(await self.model.create(
                    pad_item_id=item_id,
                    testcases_id=testcase_id
                ))

    async def delete_test_case_paditem(self, item_id: str, testcase_id: str):
        return bool(await self.model.filter(pad_item_id=item_id, testcases_id=testcase_id).delete())
