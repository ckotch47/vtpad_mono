from typing import Any

from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks

from app.src.common.crypto import bearer, user_payload
from .dto import *
from .rto import *
from .service import UserCompanyService
from ..roles_decorator import check_role_admin
from ..roles_enum import RolesEnum
from ...users.dto import RegisterUserDto

router = APIRouter(
    prefix="/v2/company-user",
    tags=["company-user"],
    responses={404: {"message": "Not found"}},
)
service = UserCompanyService()


@router.get('/list', dependencies=[Depends(bearer)], response_model=list[GetCompanyUserRto])
async def get_user_for_company(token: str = Depends(bearer)):
    await check_role_admin(user_payload(token), [RolesEnum.COMPANY_ADMIN])
    return await service.get_user_by_company(user_payload(token))


@router.put('/{user_id}', dependencies=[Depends(bearer)], response_model=bool)
async def update_user_by_company(user_id: str, dto: UpdateUserCompanyDto, token: str = Depends(bearer)):
    await check_role_admin(user_payload(token), [RolesEnum.COMPANY_ADMIN])
    return await service.update_user(user_payload(token), user_id, dto)


@router.post('', dependencies=[Depends(bearer)], response_model=GetCompanyUserRto | Any)
async def register_company_user(dto: RegisterUserDto, token: str = Depends(bearer), background_tasks: BackgroundTasks = BackgroundTasks()):
    await check_role_admin(user_payload(token), [RolesEnum.COMPANY_ADMIN])
    return await service.register_user_company(dto, user_payload(token), background_tasks)


@router.put('/{user_id}/reset-password', dependencies=[Depends(bearer)], response_model=ResetPasswordRto)
async def reset_password_company_user(user_id: str, token: str = Depends(bearer)):
    await check_role_admin(user_payload(token), [RolesEnum.COMPANY_ADMIN])
    return await service.reset_password(user_id, user_payload(token))


@router.delete('/{user_id}',  dependencies=[Depends(bearer)], include_in_schema=False)
async def delete_user(user_id: str, token: str = Depends(bearer)):
    return []
    # await check_role_admin(user_payload(token), [RolesEnum.COMPANY_ADMIN])
    # return await service.delete_user(user_id, user_payload(token))