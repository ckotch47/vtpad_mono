from typing import Union

from tortoise import Tortoise

from .model import TagModel
from .dto import *

class TagService:

    @staticmethod
    async def create_tag(space_id: str, dto: CreateTagDto):
        return await TagModel.create(
            title=dto.title,
            color=dto.color,
            space_id=space_id
        )

    @staticmethod
    async def update_tag(tag_id: str, dto: UpdateTagDto):
        await TagModel.filter(id=tag_id).update(title=dto.title, color=dto.color)
        return await TagModel.filter(id=tag_id).get()

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
        except:
            return False
