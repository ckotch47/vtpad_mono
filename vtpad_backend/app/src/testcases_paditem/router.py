from fastapi import APIRouter, Depends
from .dto import *
from ..common.crypto import bearer, user_payload
from ..spacesuser.service import SpacesUserService
from .service import TestcasesPaditemService

router = APIRouter(
    prefix="/v1/testcases-paditem",
    tags=["testcases-paditem"],
    responses={404: {"message": "Not found"}},
    deprecated=True
)

service = TestcasesPaditemService()


@router.put('/{item_id}/{testcase_id}', deprecated=True, dependencies=[Depends(bearer)], response_model=bool)
async def update_pad_item(item_id: str, testcase_id: str, token: str = Depends(bearer)):
    await SpacesUserService.check_right_edit_items(user_payload(token), item_id)
    return await service.update_test_case_paditem(item_id, testcase_id)


@router.delete('/{item_id}/{testcase_id}', deprecated=True, dependencies=[Depends(bearer)], response_model=bool)
async def delete_pad_item(item_id: str, testcase_id: str, token: str = Depends(bearer)):
    await SpacesUserService.check_right_edit_items(user_payload(token), item_id)
    return await service.delete_test_case_paditem(item_id, testcase_id)
