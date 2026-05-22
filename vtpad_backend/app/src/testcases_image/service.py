from .model import TestCaseImageModel


class TestCaseImageService:
    def __init__(self):
        self.model = TestCaseImageModel()

    async def add_image_to_case(self, case_id: str, image_id: str):
        return bool(await self.model.create(file_id=image_id, testcase_id=case_id))

    async def delete_image_from_case(self, case_id: str, image_id: str):
        return bool(await self.model.filter(file_id=image_id, testcase_id=case_id).delete())

    async def delete_all_image(self, case_id: str):
        return bool(await self.model.filter(testcase_id=case_id).delete())
