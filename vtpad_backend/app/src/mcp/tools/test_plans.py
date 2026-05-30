from ..core import mcp
from ..utils import _get_user_id, _case_to_dict
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
import logging
logger = logging.getLogger(__name__)


@mcp.tool()
async def get_test_plans(space_id: str) -> list[dict]:
    """List all test plans in a space.

    Args:
        space_id: UUID of the space

    Returns:
        List of test plans with id, name, description, case_count
    """
    plans = await TestPlanModel.filter(space_id=space_id).order_by("-created_at")
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "case_count": len(p.case_ids or []),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in plans
    ]

@mcp.tool()
async def get_test_plan(plan_id: str) -> dict | None:
    """Get a test plan by ID.

    Args:
        plan_id: UUID of the test plan

    Returns:
        Plan details or None
    """
    plan = await TestPlanService.get_by_id(plan_id)
    return {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "case_ids": plan.case_ids or [],
        "space_id": str(plan.space_id) if plan.space_id else None,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
    }

@mcp.tool()
async def create_test_plan(
    name: str,
    space_id: str,
    description: str | None = None,
    case_ids: list[str] | None = None,
) -> dict:
    """Create a new test plan.

    Args:
        name: Plan name
        space_id: Space UUID
        description: Optional description
        case_ids: Optional list of test case IDs to include

    Returns:
        Created plan details
    """
    from ...test_plan.dto import TestPlanCreateDto
    token = _get_user_id()
    dto = TestPlanCreateDto(
        name=name,
        space_id=space_id,
        description=description,
        case_ids=case_ids or [],
    )
    plan = await TestPlanService.create(dto, token)
    return {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "case_ids": plan.case_ids or [],
    }

@mcp.tool()
async def update_test_plan(
    plan_id: str,
    name: str | None = None,
    description: str | None = None,
    case_ids: list[str] | None = None,
) -> dict:
    """Update a test plan.

    Args:
        plan_id: UUID of the plan
        name: Optional new name
        description: Optional new description
        case_ids: Optional new list of case IDs (replaces existing)

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
    plan = await TestPlanService.update(plan_id, dto)
    return {
        "id": str(plan.id),
        "name": plan.name,
        "description": plan.description,
        "case_ids": plan.case_ids or [],
    }

@mcp.tool()
async def delete_test_plan(plan_id: str) -> dict:
    """Delete a test plan.

    Args:
        plan_id: UUID of the plan

    Returns:
        Success status
    """
    await TestPlanService.delete(plan_id)
    return {"deleted": True, "id": plan_id}

@mcp.tool()
async def get_test_plan_cases(plan_id: str) -> list[dict]:
    """Get all test cases in a plan.

    Args:
        plan_id: UUID of the test plan

    Returns:
        List of test cases in plan order
    """
    cases = await TestPlanService.get_cases(plan_id)
    return [_case_to_dict(c) for c in cases]
