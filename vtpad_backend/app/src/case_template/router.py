from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError

from ..common.crypto import bearer, user_payload
from ..common.right_guard import check_user_into_space
from ..test_case.service import TestCaseService
from .dto import CaseTemplateCreateDto, CaseTemplateUseDto, CaseTemplateUpdateDto
from .service import TestCaseTemplateService

class SanitizedTemplateRoute(APIRoute):
    def get_route_handler(self):
        original = super().get_route_handler()

        async def handler(request):
            try:
                return await original(request)
            except RequestValidationError:
                raise HTTPException(status_code=422, detail='Invalid case template request') from None

        return handler


router = APIRouter(prefix='/v2/test-case-template', tags=['test-case-template'], route_class=SanitizedTemplateRoute)


@router.get('/space/{space_id}', dependencies=[Depends(bearer)])
async def list_templates(
    space_id: UUID,
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
):
    await check_user_into_space(str(space_id), request)
    return await TestCaseTemplateService.list_templates(str(space_id), page, page_size)


@router.post('/space/{space_id}', dependencies=[Depends(bearer)])
async def create_template(space_id: UUID, dto: CaseTemplateCreateDto, request: Request, token: str = Depends(bearer)):
    await check_user_into_space(str(space_id), request, capability="cases")
    actor_id = user_payload(token).get('id')
    return await TestCaseTemplateService.create_template(str(space_id), dto, actor_id)


@router.get('/space/{space_id}/{template_id}', dependencies=[Depends(bearer)])
async def get_template(space_id: UUID, template_id: UUID, request: Request):
    await check_user_into_space(str(space_id), request)
    return await TestCaseTemplateService.get_template(str(space_id), str(template_id))


@router.get('/space/{space_id}/{template_id}/versions', dependencies=[Depends(bearer)])
async def list_template_versions(
    space_id: UUID, template_id: UUID, request: Request,
    page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=50),
):
    await check_user_into_space(str(space_id), request)
    return await TestCaseTemplateService.list_versions(str(space_id), str(template_id), page, page_size)


@router.get('/space/{space_id}/{template_id}/versions/{version_number}', dependencies=[Depends(bearer)])
async def get_template_version(space_id: UUID, template_id: UUID, version_number: int, request: Request):
    await check_user_into_space(str(space_id), request)
    return await TestCaseTemplateService.get_version(str(space_id), str(template_id), version_number)


@router.put('/space/{space_id}/{template_id}', dependencies=[Depends(bearer)])
async def update_template(
    space_id: UUID,
    template_id: UUID,
    dto: CaseTemplateUpdateDto,
    request: Request,
    token: str = Depends(bearer),
):
    await check_user_into_space(str(space_id), request, capability="cases")
    actor_id = user_payload(token).get('id')
    return await TestCaseTemplateService.update_template(
        str(space_id), str(template_id), dto, actor_id
    )


@router.post('/space/{space_id}/{template_id}/use', dependencies=[Depends(bearer)])
async def use_template(
    space_id: UUID,
    template_id: UUID,
    dto: CaseTemplateUseDto,
    request: Request,
    token: str = Depends(bearer),
):
    await check_user_into_space(str(space_id), request, capability="cases")
    testcase = await TestCaseTemplateService.use_template(
        str(space_id), str(template_id), dto, token
    )
    return await TestCaseService.serialize_case(testcase)
