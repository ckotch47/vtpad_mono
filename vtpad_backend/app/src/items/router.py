import uuid
from functools import wraps

from fastapi import APIRouter, Depends

from .dto import *
from .rto import *
from .service import ItemsService, ItemsServiceV2
from ..common.crypto import bearer, user_payload
from ..spacesuser.service import SpacesUserService

router = APIRouter(
    prefix="/v1/items",
    tags=["items"],
    responses={404: {"message": "Not found"}},
)


@router.get('/{pad_id}', dependencies=[Depends(bearer)], response_model=list[GetItemsRto])
async def get_items(pad_id: str):
    return await ItemsService.get_items(pad_id)


@router.post('/{pad_id}', dependencies=[Depends(bearer)], response_model=GetItemsRto)
async def create_item(pad_id: str, item: CreateItemDto, token: str = Depends(bearer)):
    await SpacesUserService.check_right_edit_pad(user_payload(token), pad_id)
    return await ItemsService.create_item(pad_id, item)


@router.put('/{item_id}', dependencies=[Depends(bearer)], response_model=bool)
async def update_item(item_id: str, item: UpdateItemDto, token: str = Depends(bearer)):
    await SpacesUserService.check_right_edit_items(user_payload(token), item_id)
    return await ItemsService.update_item(item_id, item)


@router.delete('/{item_id}', dependencies=[Depends(bearer)], response_model=bool)
async def delete_item(item_id: str, token: str = Depends(bearer)):
    await SpacesUserService.check_right_edit_items(user_payload(token), item_id)
    return await ItemsService.delete_item(item_id)


@router.patch('/{item_id}', dependencies=[Depends(bearer)], response_model=list[GetItemsRto])
async def update_path_item(item_id: str, dto: UpdateSortItemDto, token: str = Depends(bearer)):
    await SpacesUserService.check_right_edit_items(user_payload(token), item_id)
    return await ItemsService.update_path_item(item_id, dto)


routerV2 = APIRouter(
    prefix="/v2/items",
    tags=["items"],
    responses={404: {"message": "Not found"}},
)
service_v2 = ItemsServiceV2()

@routerV2.get('/{pad_id}', dependencies=[Depends(bearer)], response_model=list[GetItemsRtoV2])
async def get_items(pad_id: str):
    return await service_v2.get_items(pad_id)

@routerV2.get('/checklist/{item_id}', dependencies=[Depends(bearer)])
async def get_checklist_for_item(item_id: uuid.UUID):
    return await service_v2.get_checklist(item_id)

@routerV2.get('/testcase/{item_id}', dependencies=[Depends(bearer)])
async def get_testcase_for_item(item_id: uuid.UUID):
    return await service_v2.get_testcase(item_id)

@routerV2.post('/add/checklist/{item_id}', dependencies=[Depends(bearer)])
async def add_checklist_to_item(checklist_id: uuid.UUID, item_id: uuid.UUID):
    return await service_v2.add_checklist(item_id, checklist_id)

@routerV2.delete('/remove/checklist/{item_id}', dependencies=[Depends(bearer)])
async def remove_checklist_to_item(checklist_id: uuid.UUID, item_id: uuid.UUID):
    return await service_v2.remove_checklist(item_id, checklist_id)

@routerV2.post('/add/testcase/{item_id}', dependencies=[Depends(bearer)])
async def add_testcase_to_item(testcase_id: uuid.UUID, item_id: uuid.UUID):
    return await service_v2.add_testcase(item_id, testcase_id)

@routerV2.delete('/remove/testcase/{item_id}', dependencies=[Depends(bearer)])
async def remove_testcase_to_item(testcase_id: uuid.UUID, item_id: uuid.UUID):
    return await service_v2.remove_testcase(item_id, testcase_id)