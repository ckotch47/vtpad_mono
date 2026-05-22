from fastapi import APIRouter, Depends
from .dto import *
from ..common.crypto import bearer, user_payload
from ..spacesuser.service import SpacesUserService
from .service import TestcasesRunitemService

router = APIRouter(
    prefix="/v1/testcases-runitem",
    tags=["testcases-runitem"],
    responses={404: {"message": "Not found"}},
    deprecated=True
)
service = TestcasesRunitemService()


@router.patch('/{element_id}', dependencies=[Depends(bearer)], response_model=bool)
async def update_run_item(element_id: str, state: State, token: str = Depends(bearer)):
    # await SpacesUserService.check_right_edit_runs_item(user_payload(token), item_id)
    return await service.update_test_case_runitem(element_id, state)

