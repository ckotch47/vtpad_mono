from fastapi import HTTPException
from tortoise import Tortoise

from .model import PadFolderModel
from .dto import *
from ..pad import PadModel
from ..pad.service import PadService
from ..spacesuser.model import SpacesUserModel, SpacesUserRole


class PadFolderService:

    @staticmethod
    async def get_folders_for_space(space_id: str):
        return await PadFolderModel.filter(spaces_id=space_id, main_id=None).order_by('sort')


    @staticmethod
    async def get_folder_detail(folder_id: str):
        temp = await PadFolderModel.filter(id=folder_id).get()
        return {
            "id": temp.id,
            "name": temp.name,
            "sort": temp.sort,
            "spaces": temp.__getattribute__('spaces_id'),
            "main_id": temp.__getattribute__('main_id'),
            "pad": await PadService.get_pad_by_folder(folder_id),
            "folder": await PadFolderModel.filter(main_id=folder_id)
        }

    @staticmethod
    async def create_folder(space_id: str, dto: CreatePadFolderDto):
        last_sort = await PadFolderModel.filter(spaces_id=space_id).order_by('-sort').first()
        try:
            sort = ((last_sort.sort / 10) + 1) * 10
        except Exception:
            sort = 10

        try:
            if dto.main_id:
                return await PadFolderModel.create(
                    name=dto.name,
                    sort=int(sort),
                    spaces_id=space_id,
                    main_id=dto.main_id
                )
            return await PadFolderModel.create(
                name=dto.name,
                sort=int(sort),
                spaces_id=space_id
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')

    @staticmethod
    async def update_folder(folder_id: str, dto: UpdatePadFolderDto):
        try:
            await PadFolderModel.filter(id=folder_id).update(name=dto.name)
            return await PadFolderService.get_folder_detail(folder_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')

    @staticmethod
    async def delete_folder(folder_id: str):
        try:
            return bool(await PadFolderModel.filter(id=folder_id).delete())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')


    @staticmethod
    async def check_right_edit_folder(space_id: str = None, folder_id: str = None, user_payload: dict = None):
        if not user_payload:
            raise HTTPException(status_code=403, detail=f'not right')

        if space_id:
            temp = await SpacesUserModel.filter(userId=str(user_payload.get('id')), spaceId=space_id).get()
            if temp.role != SpacesUserRole.owner:
                if 'editPads' in temp.right and temp.right['editPads']:
                    pass
                else:
                    raise HTTPException(status_code=403, detail="not have right")

        if folder_id:
            conn = Tortoise.get_connection("default")
            result = await conn.execute_query_dict(
                'SELECT su.role, su."right" FROM padfoldermodel ' 
                'LEFT JOIN spacesusermodel su on padfoldermodel.spaces_id = su."spaceId" '
                "WHERE padfoldermodel.id = $1 "
                "AND su.\"userId\" = $2",
                [folder_id, user_payload.get('id')]
            )
            if not result:
                raise HTTPException(status_code=404, detail="not found")
            temp = result[0]

            if temp['role'] != SpacesUserRole.owner:
                if 'editPads' in temp['right'] and temp['right']['editPads']:
                    pass
                else:
                    raise HTTPException(status_code=403, detail="not have right")
