from fastapi import HTTPException
from tortoise.transactions import in_transaction

from .model import TagModel
from .dto import *
from ..space.model import SpaceModel

class TagService:

    @staticmethod
    async def create_tag(space_id: str, dto: CreateTagDto):
        title = dto.title.strip()
        if not title or len(title) > 255:
            raise HTTPException(status_code=422, detail="tag title must contain 1 to 255 characters")
        async with in_transaction() as connection:
            space = await SpaceModel.filter(id=space_id).using_db(connection).select_for_update().first()
            if not space:
                raise HTTPException(status_code=404, detail="Space not found")
            rows = await connection.execute_query_dict(
                "SELECT id FROM tagmodel WHERE space_id = $1 AND lower(btrim(title)) = $2 "
                "ORDER BY (title = $3) DESC, create_date ASC, id ASC LIMIT 1",
                [space_id, title.lower(), title],
            )
            if rows:
                return await TagModel.filter(id=rows[0]["id"]).using_db(connection).first()
            return await TagModel.create(
                title=title,
                color=dto.color,
                space_id=space_id,
                using_db=connection,
            )

    @staticmethod
    async def update_tag(tag_id: str, dto: UpdateTagDto):
        title = dto.title.strip()
        if not title or len(title) > 255:
            raise HTTPException(status_code=422, detail="tag title must contain 1 to 255 characters")
        existing = await TagModel.get_or_none(id=tag_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Tag not found")
        async with in_transaction() as connection:
            await SpaceModel.filter(id=existing.space_id).using_db(connection).select_for_update().first()
            current = await TagModel.filter(id=tag_id).using_db(connection).select_for_update().first()
            if not current:
                raise HTTPException(status_code=404, detail="Tag not found")
            duplicates = await connection.execute_query_dict(
                "SELECT id FROM tagmodel WHERE space_id = $1 AND id <> $2 "
                "AND lower(btrim(title)) = $3 ORDER BY create_date ASC, id ASC LIMIT 1",
                [str(current.space_id), tag_id, title.lower()],
            )
            if duplicates:
                raise HTTPException(status_code=409, detail="A tag with this title already exists in the Space")
            await TagModel.filter(id=tag_id).using_db(connection).update(title=title, color=dto.color)
            return await TagModel.filter(id=tag_id).using_db(connection).first()

    @staticmethod
    async def get_tag(space_id: str):
        res = []
        tmp = await TagModel.filter(space_id=space_id).all()
        for i in tmp:
            res.append(i.__dict__)
        return res

    @staticmethod
    async def delete_tag(tag_id: str):
        try:
            await TagModel.filter(id=tag_id).delete()
            return True
        except Exception:
            return False
