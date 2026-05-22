from functools import wraps

from fastapi import APIRouter, Depends
from .service import SpaceService
from .dto import *
from .rto import *
from ..admin.roles_decorator import check_role_admin
from ..admin.roles_enum import RolesEnum
from ..common.crypto import bearer, user_payload
from ..common.right_guard import check_user_into_space

router = APIRouter(
    prefix="/v1/space",
    tags=["space"],
    responses={404: {"message": "Not found"}},
)

space_service = SpaceService()


def check_owner(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await space_service.check_owner(user_payload(kwargs.get('token')), kwargs.get('space_id'))
        return await func(*args, **kwargs)

    return wrapper


@router.get('', dependencies=[Depends(bearer)], response_model=list[GetSpaceRto] | Any,
            response_model_exclude_none=True)
async def get_space(token: str = Depends(bearer)):
    return await space_service.get_space(user_payload(token))


@router.post('', dependencies=[Depends(bearer)], response_model=GetSpaceRto, response_model_exclude_none=True)
async def create_space(space: CreateSpaceDto, token: str = Depends(bearer)):
    await check_role_admin(user_payload(token), [RolesEnum.COMPANY_ADMIN])
    return await space_service.create_space(space, user_payload(token))


@router.get('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=GetSpaceByIdRto | Any,
            response_model_exclude_none=False)
async def get_space_by_id(space_id: str, token: str = Depends(bearer)):
    return await space_service.get_space_by_id(user_payload(token), space_id)


@router.get('/{space_id}/users', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[GetUserForSpaceRto] | Any)
async def get_space_user_by_id(space_id: str):
    return await space_service.get_user_for_space(space_id)


@router.put('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=bool)
@check_owner
async def update_space(space_id: str, space: UpdateSpaceDto, token: str = Depends(bearer)):
    return await space_service.update_space(space_id, space, user_payload(token))


@router.put('/{space_id}/user', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[GetUserForSpaceRto] | Any)
@check_owner
async def update_space_user(space_id: str, mail: AddUserSpaceDto, token: str = Depends(bearer)):
    return await space_service.add_user_space(space_id, mail, user_payload(token))


@router.delete('/{space_id}/user/{user_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[GetUserForSpaceRto] | Any)
@check_owner
async def delete_space_user_id(space_id: str, user_id: str, token: str = Depends(bearer)):
    return await space_service.delete_user_from_space(user_id, space_id, user_payload(token))


@router.patch('/{space_id}/user/{user_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=list[GetUserForSpaceRto] | Any)
@check_owner
async def update_user_rules_in_space(space_id: str, user_id: str,
                                     dto: UpdateUserRulesForSpaceDto, token: str = Depends(bearer)):
    return await space_service.update_user_rules_in_space(space_id, user_id, dto)


@router.put('/{space_id}/user-make-owner/{user_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)],
            response_model=list[GetUserForSpaceRto] | Any)
@check_owner
async def make_user_owner_space(space_id: str, user_id: str, token: str = Depends(bearer)):
    return await space_service.make_user_owner_to_space(space_id, user_id)


@router.delete('/{space_id}', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=bool)
@check_owner
async def delete_space(space_id: str, token: str = Depends(bearer)):
    return await space_service.delete_space(space_id)


@router.get('/{space_id}/all_runs', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=GetAllRunsForSpaceRto)
async def get_all_runs_spaces(space_id: str):
    return await space_service.get_all_runs_spaces(space_id)


@router.get('/{space_id}/statistic', dependencies=[Depends(bearer), Depends(check_user_into_space)], response_model=GetStatisticRto)
async def get_statistic_for_space(space_id: str):
    return await space_service.get_statistic_for_space(space_id)

@router.get('/by-short/{short_name}', dependencies=[Depends(bearer)])
async def get_space_by_short_name(short_name: str, token=Depends(bearer)):
    return await space_service.get_by_short_name(short_name, user_payload(token))