from fastapi import HTTPException
from tortoise import Tortoise

from .model import SpacesUserModel, SpacesUserRole
from ..items import ItemsModel
from ..notes import NotesModel
from ..pad import PadModel


class SpacesUserService:
    @staticmethod
    async def check_right(user_payload: dict, right: str):
        user_id = str(user_payload.get('id'))
        try:
            temp = await SpacesUserModel.filter(userId=user_id).get()
        except Exception:
            raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_edit_pad(user_payload: dict, pad_id: str):
        temp = (await PadModel.filter(id=pad_id).get()).__dict__
        spaces_id = temp.get('spaces_id')
        temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=spaces_id).get()
        if temp.role != SpacesUserRole.owner:
            if 'editPads' in temp.right and temp.right['editPads']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_edit_items(user_payload: dict, item_id: str):
        temp_item = (await ItemsModel.filter(id=item_id).get()).__dict__
        temp_pad = (await PadModel.filter(id=str(temp_item.get('pad_id'))).get()).__dict__
        spaces_id = temp_pad.get('spaces_id')

        temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=spaces_id).get()
        if temp.role != SpacesUserRole.owner:
            if 'editItems' in temp.right and temp.right['editItems']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_runs(user_payload: dict, run_id: str):
        conn = Tortoise.get_connection("default")
        run: dict = (await conn.execute_query_dict(
            "SELECT s.id FROM runmodel "
            "LEFT JOIN padmodel p on runmodel.pads_id = p.id "
            "LEFT JOIN spacemodel s on p.spaces_id = s.id "
            "WHERE runmodel.id = $1",
            [run_id]
        ))[0]
        spaces_id = str(run.get('id'))
        temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=spaces_id).get()

        if temp.role != SpacesUserRole.owner:
            if 'editRuns' in temp.right and temp.right['editRuns']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")

    @staticmethod
    async def check_right_edit_runs_item(user_payload: dict, item_id: str):
        conn = Tortoise.get_connection("default")
        spaces_id = (await conn.execute_query_dict(
            "SELECT s.id FROM runitemsmodel "
            "LEFT JOIN runmodel r on runitemsmodel.run_id = r.id "
            "LEFT JOIN padmodel p on r.pads_id = p.id "
            "LEFT JOIN spacemodel s on p.spaces_id = s.id "
            "WHERE runitemsmodel.id = $1",
            [item_id]
        ))[0]
        temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=str(spaces_id.get('id'))).get()

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
        temp = (await conn.execute_query_dict(
            'SELECT sm."right", sm.role FROM tagmodel '
            'LEFT JOIN spacesusermodel sm on sm."spaceId" = tagmodel.space_id '
            "WHERE tagmodel.id = $1 "
            'AND sm."userId" = $2',
            [tag_id, user_payload.get('id')]
        ))[0]
        if temp.get('role') != SpacesUserRole.owner:
            if 'editTags' in temp.get('right') and temp.get('right')['editTags']:
                pass
            else:
                raise HTTPException(status_code=403, detail="not have right")