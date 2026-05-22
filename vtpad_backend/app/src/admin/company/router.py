from fastapi import APIRouter, Depends

from .dto import *
from app.src.common.crypto import bearer, user_payload
from .rto import *
from .service import CompanyService
from ..roles_decorator import check_role_admin
from ..roles_enum import RolesEnum
from app.src.space.rto import *

router = APIRouter(
    prefix="/v2/amin/company",
    tags=["admin"],
    responses={404: {"message": "Not found"}},
    include_in_schema=False
)
service = CompanyService()


@router.get('/list', dependencies=[Depends(bearer)], name='get_company_list', response_model=list[CompanyRto])
async def get_company_list(dto: GetCompanyListDto = Depends(GetCompanyListDto), token: str = Depends(bearer)):
    await check_role_admin(user_payload(token), [RolesEnum.MAIN_ADMIN])
    return await service.get_company_list(dto)


@router.post('', dependencies=[Depends(bearer)], response_model=CompanyRto)
async def add_company(dto: AddCompanyDto, token: str = Depends(bearer)):
    await check_role_admin(user_payload(token), [RolesEnum.MAIN_ADMIN])
    return await service.create_company(dto)


@router.put('/{company_id}', dependencies=[Depends(bearer)], response_model=CompanyRto)
async def update_company(company_id: str, dto: UpdateCompanyDto, token: str = Depends(bearer)):
    await check_role_admin(user_payload(token), [RolesEnum.MAIN_ADMIN])
    return await service.update_company(dto, company_id)


@router.get('/detail/{company_id}')
async def get_company_detail():
    return []


router_company_admin = APIRouter(
    prefix="/v1/company",
    tags=["company"],
    responses={404: {"message": "Not found"}},
)

@router_company_admin.get('/spaces', dependencies=[Depends(bearer)], response_model=GetSpaceRto | Any)
async def get_spaces_for_company(token: str = Depends(bearer)):
    await check_role_admin(user_payload(token), [RolesEnum.MAIN_ADMIN, RolesEnum.COMPANY_ADMIN])
    return await service.get_space_for_company( user_payload(token))
