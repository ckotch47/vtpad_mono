from ..core import mcp
from ..utils import _get_user_id, _cases_to_dict_with_metadata
from fastmcp.server.dependencies import get_http_request

from ...api_token.service import ApiTokenService
from ...test_case.model import TestCaseModel, TestCaseStatus, TestCaseType
from ...test_case.service import TestCaseService
from ...test_suite.model import TestSuiteModel
from ...test_suite.service import TestSuiteService
from ...section.model import SectionModel
from ...section.service import SectionService
from ...embedding.service import EmbeddingService
from ...tech_doc.model import TechDocModel
from ...tech_doc.service import TechDocService
from ...test_run.model import TestRunModel, TestResultModel, TestRunStatus, TestResultStatus
from ...space.model import SpaceModel
from ...test_run.service import TestRunService, TestResultService
from ...test_run.dto import TestRunCreateDto, TestResultUpdateDto
from ...test_case.dto import TestCaseUpdateDto
from ...test_suite.dto import TestSuiteUpdateDto
from ...section.dto import SectionUpdateDto
from ...test_plan.model import TestPlanModel
from ...test_plan.service import TestPlanService
from ...analytics.service import AnalyticsService
from ...common.right_guard import check_user_into_space
import logging
logger = logging.getLogger(__name__)


@mcp.tool()
async def get_test_plans(space_id: str) -> list[dict]:
    """List all test plans in a space.

    Args:
        space_id: UUID of the space

    Returns:
        List of test plans with source IDs, filters, and resolved case_count
    """
    request = get_http_request()
    await check_user_into_space(str(space_id), request)
    plans = await TestPlanModel.filter(space_id=space_id).order_by("-created_at")
    result = []
    for plan in plans:
        result.append({
            "id": str(plan.id),
            "name": plan.name,
            "description": plan.description,
            "suite_ids": plan.suite_ids or [],
            "case_ids": plan.case_ids or [],
            "filters": plan.filters or {},
            "case_count": await TestPlanService.count_cases(str(plan.id)),
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
        })
    return result

@mcp.tool()
async def get_test_plan(plan_id: str) -> dict | None:
    """Get a test plan by ID.

    Args:
        plan_id: UUID of the test plan

    Returns:
        Plan details or None
    """
    plan = await TestPlanService.get_by_id(plan_id, request=get_http_request())
    return {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "case_ids": plan.case_ids or [],
        "suite_ids": plan.suite_ids or [],
        "filters": plan.filters or {},
        "space_id": str(plan.space_id) if plan.space_id else None,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
    }

@mcp.tool()
async def create_test_plan(
    name: str,
    space_id: str,
    description: str | None = None,
    case_ids: list[str] | None = None,
    suite_ids: list[str] | None = None,
    filters: dict | None = None,
) -> dict:
    """Create a new test plan.

    Args:
        name: Plan name
        space_id: Space UUID
        description: Optional description
        case_ids: Optional list of test case IDs to include
        suite_ids: Optional list of test suite IDs to include
        filters: Optional priority, tag, and typed custom-field filters

    Returns:
        Created plan details
    """
    from ...test_plan.dto import TestPlanCreateDto
    request = get_http_request()
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    dto = TestPlanCreateDto(
        name=name,
        space_id=space_id,
        description=description,
        case_ids=case_ids or [],
        suite_ids=suite_ids or [],
        filters=filters or {},
    )
    plan = await TestPlanService.create(dto, token, request)
    return {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "case_ids": plan.case_ids or [],
        "suite_ids": plan.suite_ids or [],
        "filters": plan.filters or {},
    }

@mcp.tool()
async def update_test_plan(
    plan_id: str,
    name: str | None = None,
    description: str | None = None,
    case_ids: list[str] | None = None,
    suite_ids: list[str] | None = None,
    filters: dict | None = None,
) -> dict:
    """Update a test plan.

    Args:
        plan_id: UUID of the plan
        name: Optional new name
        description: Optional new description
        case_ids: Optional new list of case IDs (replaces existing)
        suite_ids: Optional new list of suite IDs (replaces existing)
        filters: Optional filters; pass {} to clear them

    Returns:
        Updated plan details
    """
    from ...test_plan.dto import TestPlanUpdateDto
    dto = TestPlanUpdateDto()
    if name is not None:
        dto.name = name
    if description is not None:
        dto.description = description
    if case_ids is not None:
        dto.case_ids = case_ids
    if suite_ids is not None:
        dto.suite_ids = suite_ids
    if filters is not None:
        dto.filters = filters
    plan = await TestPlanService.update(plan_id, dto, get_http_request())
    return {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "case_ids": plan.case_ids or [],
        "suite_ids": plan.suite_ids or [],
        "filters": plan.filters or {},
    }

@mcp.tool()
async def delete_test_plan(plan_id: str) -> dict:
    """Delete a test plan.

    Args:
        plan_id: UUID of the plan

    Returns:
        Success status
    """
    await TestPlanService.delete(plan_id, get_http_request())
    return {"deleted": True, "id": plan_id}


@mcp.tool()
async def preview_test_plan_selection(
    space_id: str,
    suite_ids: list[str] | None = None,
    case_ids: list[str] | None = None,
    filters: dict | None = None,
) -> dict:
    """Preview the selected testcase count for a plan draft without saving it.

    Args:
        space_id: UUID of the space
        suite_ids: Optional suite source IDs; their cases are unioned with explicit case_ids
        case_ids: Optional explicitly selected testcase IDs
        filters: Optional intersecting priorities, all-tags, and typed custom-field filters

    Returns:
        Total selected case count, a bounded list of IDs, and whether IDs were truncated
    """
    from ...test_plan.dto import TestPlanPreviewDto

    request = get_http_request()
    dto = TestPlanPreviewDto(
        space_id=space_id,
        suite_ids=suite_ids or [],
        case_ids=case_ids or [],
        filters=filters or {},
    )
    return await TestPlanService.preview_selection(dto, request)

@mcp.tool()
async def get_test_plan_cases(plan_id: str) -> list[dict]:
    """Get all test cases in a plan.

    Args:
        plan_id: UUID of the test plan

    Returns:
        List of test cases in plan order
    """
    request = get_http_request()
    plan = await TestPlanService.get_by_id(plan_id, request=request)
    cases = await TestPlanService.get_cases(plan_id, request=request)
    return await _cases_to_dict_with_metadata(cases)
