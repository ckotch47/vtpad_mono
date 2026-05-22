from fastapi import HTTPException

from .model import PadModel
from .dto import *


async def get_last_sort_pad(space_id: str, folder_id: str = None):
    last_sort = await PadModel.filter(spaces_id=space_id, folder_id=folder_id).order_by('-sort').first()
    try:
        sort = ((last_sort.sort / 10) + 1) * 10
    except Exception as e:
        sort = 10
    return int(sort)


class PadService:
    @staticmethod
    async def create_pad(space_id: str, pad: CreatePadDto):
        if not pad.folder_id:
            temp = await PadModel.create(
                name=pad.name,
                sort=await get_last_sort_pad(space_id),
                spaces_id=space_id,
            )
        else:
            temp = await PadModel.create(
                name=pad.name,
                sort=await get_last_sort_pad(space_id, pad.folder_id),
                spaces_id=space_id,
                folder_id=pad.folder_id
            )
        return temp

    @staticmethod
    async def get_pad(space_id: str, folder_id: str = None):
        if not folder_id:
            temp = await PadModel.filter(spaces_id=space_id, folder_id=None).order_by('sort')
        else:
            temp = await PadModel.filter(spaces_id=space_id, folder_id=folder_id).order_by('sort')
        return temp

    @staticmethod
    async def get_pad_detail(pad_id: str):
        return await PadModel.filter(id=pad_id).get()

    @staticmethod
    async def get_all_pad(space_id: str):
        return await PadModel.filter(spaces_id=space_id).order_by('sort')

    @staticmethod
    async def get_pad_by_folder(folder_id: str):
        return await PadModel.filter(folder_id=folder_id).order_by('sort')

    @staticmethod
    async def update_pad(pad_id: str, pad: UpdatePadDto):
        try:
            temp_pad = await PadModel.filter(id=pad_id).get()
            if pad.name:
                await PadModel.filter(id=pad_id).update(name=pad.name)
            if pad.folder_id and pad.folder_id != 'none':
                await PadModel.filter(id=pad_id).update(
                    folder_id=pad.folder_id,
                    # sort=await get_last_sort_pad(temp_pad.spaces_id, pad.folder_id)
                )
            if pad.folder_id == 'none':
                await PadModel.filter(id=pad_id).update(
                    folder_id=None,
                    # sort=await get_last_sort_pad(temp_pad.spaces_id)
                )
            return await PadModel.filter(id=pad_id).get()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")

    @staticmethod
    async def delete_pad(pad_id: str):
        return bool(await PadModel.filter(id=pad_id).delete())


    @staticmethod
    async def update_sort_pad(pad_id: str, dto: UpdateSortPadDto):
        temp = None
        if dto.sortBeforeId:
            temp = await PadModel.filter(id=dto.sortBeforeId).get()
            temp1 = await PadModel.filter(id=pad_id).get()
            await PadModel.filter(id=dto.sortBeforeId).update(sort=temp1.sort)
            await PadModel.filter(id=pad_id).update(sort=temp.sort)
        if dto.sortAfterId:
            temp = await PadModel.filter(id=dto.sortAfterId).get()
            temp1 = await PadModel.filter(id=pad_id).get()
            await PadModel.filter(id=dto.sortAfterId).update(sort=temp1.sort)
            await PadModel.filter(id=pad_id).update(sort=temp.sort)

        try:
            return await PadService.get_pad(str(temp.spaces_id))
        except:
            return True
