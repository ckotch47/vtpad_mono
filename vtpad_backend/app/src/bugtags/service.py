from fastapi import HTTPException
from tortoise import Tortoise

from .model import BugTagsModel
from ..tag import TagModel


class BugTagsService:
    @staticmethod
    async def add_bug_tag(bug_id: str, tag_id: str):
        try:
            await BugTagsModel.create(
                bug_id=bug_id,
                tag_id=tag_id
            )
            return await TagModel.filter(id=tag_id).get()
        except Exception:
            raise HTTPException(status_code=400, detail="not save")

    @staticmethod
    async def delete_tag_from_bug(bug_id: str, tag_id: str):
        return bool(await BugTagsModel.filter(bug_id=bug_id, tag_id=tag_id).delete())

    @staticmethod
    async def get_tags_fo_bug(bug_id: str):
        conn = Tortoise.get_connection("default")
        return await conn.execute_query_dict(
            "SELECT t.id, t.title, t.color FROM bugtagsmodel "
            "LEFT JOIN tagmodel t on bugtagsmodel.tag_id = t.id "
            "WHERE bug_id = $1",
            [bug_id]
        )
