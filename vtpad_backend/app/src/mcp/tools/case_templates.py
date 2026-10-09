from uuid import UUID
from pydantic import ValidationError
from fastapi import HTTPException

from fastmcp.server.dependencies import get_http_request

from ..core import mcp
from ..utils import _get_user_id
from ...case_template.dto import CaseTemplateCreateDto, CaseTemplateUseDto, CaseTemplateUpdateDto
from ...case_template.service import TestCaseTemplateService
from ...common.right_guard import check_user_into_space
from ...test_case.service import TestCaseService


async def _require_space_access(space_id: str) -> None:
    await check_user_into_space(space_id, get_http_request())


def _validated(model, **values):
    try:
        return model(**values)
    except ValidationError:
        raise HTTPException(status_code=422, detail='Invalid case template request') from None


@mcp.tool()
async def list_test_case_templates(space_id: UUID, page: int = 1, page_size: int = 50) -> dict:
    """List versioned case templates in an accessible space."""
    await _require_space_access(str(space_id))
    return await TestCaseTemplateService.list_templates(str(space_id), page, page_size)


@mcp.tool()
async def get_test_case_template(space_id: UUID, template_id: UUID) -> dict:
    """Get a template and its immutable versions from the requested space."""
    await _require_space_access(str(space_id))
    return await TestCaseTemplateService.get_template(str(space_id), str(template_id))


@mcp.tool()
async def list_test_case_template_versions(space_id: UUID, template_id: UUID, page: int = 1, page_size: int = 20) -> dict:
    """List bounded metadata for immutable case template versions."""
    await _require_space_access(str(space_id))
    return await TestCaseTemplateService.list_versions(str(space_id), str(template_id), page, page_size)


@mcp.tool()
async def get_test_case_template_version(space_id: UUID, template_id: UUID, version_number: int) -> dict:
    """Get one immutable version's allowlisted content."""
    await _require_space_access(str(space_id))
    return await TestCaseTemplateService.get_version(str(space_id), str(template_id), version_number)


@mcp.tool()
async def create_test_case_template(
    space_id: UUID,
    name: str,
    title: str,
    description: str | None = None,
    text: str | None = None,
    preconditions: str | None = None,
    steps: str | None = None,
    expected_results: str | None = None,
    postconditions: str | None = None,
    type: str = 'manual',
    priority: str = 'P2',
    estimated_duration_seconds: int | None = None,
) -> dict:
    """Create template version 1 with allowlisted case fields."""
    await _require_space_access(str(space_id))
    dto = _validated(CaseTemplateCreateDto,
        name=name,
        description=description,
        fields={
            'title': title, 'text': text, 'preconditions': preconditions, 'steps': steps,
            'expected_results': expected_results, 'postconditions': postconditions,
            'type': type, 'priority': priority,
            'estimated_duration_seconds': estimated_duration_seconds,
        },
    )
    return await TestCaseTemplateService.create_template(str(space_id), dto, _get_user_id())


@mcp.tool()
async def update_test_case_template(
    space_id: UUID,
    template_id: UUID,
    name: str,
    title: str,
    description: str | None = None,
    text: str | None = None,
    preconditions: str | None = None,
    steps: str | None = None,
    expected_results: str | None = None,
    postconditions: str | None = None,
    type: str = 'manual',
    priority: str = 'P2',
    estimated_duration_seconds: int | None = None,
) -> dict:
    """Update metadata and append an immutable content version when fields change."""
    await _require_space_access(str(space_id))
    dto = _validated(CaseTemplateUpdateDto,
        name=name,
        description=description,
        fields={
            'title': title, 'text': text, 'preconditions': preconditions, 'steps': steps,
            'expected_results': expected_results, 'postconditions': postconditions,
            'type': type, 'priority': priority,
            'estimated_duration_seconds': estimated_duration_seconds,
        },
    )
    return await TestCaseTemplateService.update_template(
        str(space_id), str(template_id), dto, _get_user_id()
    )


@mcp.tool()
async def use_test_case_template(
    space_id: UUID,
    template_id: UUID,
    title: str,
    suite_id: UUID | None = None,
    section_id: UUID | None = None,
    version_number: int | None = None,
    override_text: str | None = None,
    override_preconditions: str | None = None,
    override_steps: str | None = None,
    override_expected_results: str | None = None,
    override_postconditions: str | None = None,
    override_type: str | None = None,
    override_priority: str | None = None,
    override_estimated_duration_seconds: int | None = None,
    custom_fields: list[dict] | None = None,
) -> dict:
    """Create a new case from a selected immutable template version."""
    await _require_space_access(str(space_id))
    request = get_http_request()
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    dto = _validated(CaseTemplateUseDto,
        title=title, suite_id=suite_id, section_id=section_id,
        version_number=version_number, overrides={
            'text': override_text, 'preconditions': override_preconditions,
            'steps': override_steps, 'expected_results': override_expected_results,
            'postconditions': override_postconditions, 'type': override_type,
            'priority': override_priority,
            'estimated_duration_seconds': override_estimated_duration_seconds,
        },
        custom_fields=custom_fields,
    )
    testcase = await TestCaseTemplateService.use_template(
        str(space_id), str(template_id), dto, token
    )
    return await TestCaseService.serialize_case(testcase)
