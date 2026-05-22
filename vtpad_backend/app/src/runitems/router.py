from fastapi import APIRouter, Depends
from .service import RunItemsService
from .dto import *
from ..common.crypto import bearer, user_payload
from ..spacesuser.service import SpacesUserService

router = APIRouter(
    prefix="/v1/runitems",
    tags=["runitems"],
    responses={404: {"message": "Not found"}},
)


@router.patch('/{item_id}', dependencies=[Depends(bearer)], response_model=bool)
async def update_run_item(item_id: str, state: State, token: str = Depends(bearer)):
    await SpacesUserService.check_right_edit_runs_item(user_payload(token), item_id)
    return await RunItemsService.update_run_item(item_id, state)
