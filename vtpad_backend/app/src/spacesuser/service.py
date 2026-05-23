from fastapi import HTTPException
from tortoise import Tortoise

from .model import SpacesUserModel, SpacesUserRole
from ..notes import NotesModel


class SpacesUserService:
    @staticmethod
    async def check_right(user_payload: dict, right: str):
        user_id = str(user_payload.get('id'))
        try:
            temp = await SpacesUserModel.filter(userId=user_id).get()
        except Exception:
            raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_edit_test_suite(user_payload: dict, suite_id: str):
        from ..test_suite.model import TestSuiteModel
        suite = await TestSuiteModel.get_or_none(id=suite_id)
        if not suite:
            raise HTTPException(status_code=404, detail="not found")
        spaces_id = str(suite.space_id)
        temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=spaces_id).get()
        if temp.role != SpacesUserRole.owner:
            if 'editPads' in temp.right and temp.right['editPads']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_edit_section(user_payload: dict, section_id: str):
        from ..section.model import SectionModel
        from ..test_suite.model import TestSuiteModel
        section = await SectionModel.get_or_none(id=section_id)
        if not section:
            raise HTTPException(status_code=404, detail="not found")
        suite = await TestSuiteModel.get_or_none(id=str(section.suite_id))
        spaces_id = str(suite.space_id) if suite else None
        if not spaces_id:
            raise HTTPException(status_code=404, detail="not found")
        temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=spaces_id).get()
        if temp.role != SpacesUserRole.owner:
            if 'editItems' in temp.right and temp.right['editItems']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_test_run(user_payload: dict, run_id: str):
        from ..test_run.model import TestRunModel
        run = await TestRunModel.get_or_none(id=run_id)
        if not run:
            raise HTTPException(status_code=404, detail="not found")
        spaces_id = str(run.space_id)
        temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=spaces_id).get()
        if temp.role != SpacesUserRole.owner:
            if 'editRuns' in temp.right and temp.right['editRuns']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_test_result(user_payload: dict, result_id: str):
        from ..test_run.model import TestResultModel, TestRunModel
        result = await TestResultModel.get_or_none(id=result_id)
        if not result:
            raise HTTPException(status_code=404, detail="not found")
        run = await TestRunModel.get_or_none(id=str(result.run_id))
        spaces_id = str(run.space_id) if run else None
        if not spaces_id:
            raise HTTPException(status_code=404, detail="not found")
        temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=spaces_id).get()
        if temp.role != SpacesUserRole.owner:
            if 'editRuns' in temp.right and temp.right['editRuns']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_add_tags(user_payload: dict, space_id: str):
        temp = (await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=str(space_id)))[0]
        if temp.role != SpacesUserRole.owner:
            if 'editTags' in temp.right and temp.right['editTags']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_edit_tags(user_payload: dict, tag_id: str):
        conn = Tortoise.get_connection("default")
        result = await conn.execute_query_dict(
            'SELECT sm."right", sm.role FROM tagmodel '
            'LEFT JOIN spacesusermodel sm on sm."spaceId" = tagmodel.space_id '
            "WHERE tagmodel.id = $1 "
            'AND sm."userId" = $2',
            [tag_id, user_payload.get('id')]
        )
        if not result:
            raise HTTPException(status_code=404, detail="not found")
        temp = result[0]
        if temp.get('role') != SpacesUserRole.owner:
            if 'editTags' in temp.get('right') and temp.get('right')['editTags']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")
