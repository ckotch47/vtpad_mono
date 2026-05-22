
from fastapi import APIRouter, Depends
from .dto import *
from .service import UserService

from ..common.crypto import bearer, user_payload

from .rto import *
router = APIRouter(
    prefix="/v1/user",
    tags=["user"],
    responses={404: {"message": "Not found"}},
)


@router.post('', response_model=RegisterUserRto, deprecated=True)
async def register_user(user: RegisterUserDto):
    return [] #await UserService.create_user(user)


@router.get('', dependencies=[Depends(bearer)], response_model=UserRto)
async def get_user(token: str = Depends(bearer)):
    return await UserService.get_user_by_id(user_payload(token))


@router.patch('', dependencies=[Depends(bearer)], response_model=UserRto)
async def update_user(user: UpdateUserDto, token: str = Depends(bearer)):
    return await UserService.update_user(user, user_payload(token))


@router.get('/search/by-mail', dependencies=[Depends(bearer)], response_model=list[SearchUserByMail])
async def search_user_by_mail(mail: str, token: str = Depends(bearer)):
    return await UserService.search_user_by_mail(mail, user_payload(token))


routerV2 = APIRouter(
    prefix="/v2/user",
    tags=["user"],
    responses={404: {"message": "Not found"}},
)

@routerV2.get('', dependencies=[Depends(bearer)])
async def get_user(token: str = Depends(bearer)):
    return await UserService.get_user_by_id_V2(user_payload(token))