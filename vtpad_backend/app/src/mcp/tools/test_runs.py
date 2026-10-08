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
from ...common.right_guard import check_user_into_space
import logging
logger = logging.getLogger(__name__)


async def _transition_run(run_id: str, action: str) -> dict:
    request = get_http_request()
    run = await TestRunService.get_by_id(run_id)
    await check_user_into_space(str(run.space_id), request)
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    transition = getattr(TestRunService, action)
    updated = await transition(run_id, token)
    return {
        'id': str(updated.id),
        'status': updated.status.value if hasattr(updated.status, 'value') else updated.status,
        'started_at': updated.started_at.isoformat() if updated.started_at else None,
        'completed_at': updated.completed_at.isoformat() if updated.completed_at else None,
        'timer': await TestRunService.get_timer(run_id),
    }


@mcp.tool()
async def start_test_run(run_id: str) -> dict:
    """Start a draft run and its shared timer."""
    return await _transition_run(run_id, 'start')


@mcp.tool()
async def pause_test_run(run_id: str) -> dict:
    """Pause the shared timer for an active run."""
    return await _transition_run(run_id, 'pause')


@mcp.tool()
async def resume_test_run(run_id: str) -> dict:
    """Resume the shared timer for a paused run."""
    return await _transition_run(run_id, 'resume')


@mcp.tool()
async def complete_test_run(run_id: str) -> dict:
    """Complete an active run and close its timer interval."""
    return await _transition_run(run_id, 'complete')


@mcp.tool()
async def create_test_run(
    space_id: str,
    suite_id: str,
    name: str,
    description: str | None = None,
    environment_id: str | None = None,
    milestone_id: str | None = None,
) -> dict:
    """Create a new test run from a test suite.

    Args:
        space_id: UUID of the space
        suite_id: UUID of the test suite
        name: Name of the test run
        description: Optional description
        environment_id: Optional environment UUID
        milestone_id: Optional milestone UUID

    Returns:
        Created test run details
    """
    request = get_http_request()
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    await check_user_into_space(space_id, request)
    dto = TestRunCreateDto(
        space_id=space_id,
        suite_id=suite_id,
        name=name,
        description=description,
        environment_id=environment_id,
        milestone_id=milestone_id,
    )
    run = await TestRunService.create(dto, token)
    return {
        "id": str(run.id),
        "name": run.name,
        "status": run.status.value if hasattr(run.status, "value") else run.status,
        "suite_id": str(run.suite_id) if run.suite_id else None,
        "space_id": str(run.space_id) if run.space_id else None,
    }

@mcp.tool()
async def get_run_results(run_id: str) -> dict | None:
    """Get test run results with statistics.

    Args:
        run_id: UUID of the test run

    Returns:
        Run details, stats, and results
    """
    try:
        request = get_http_request()
        run = await TestRunService.get_by_id(run_id)
        await check_user_into_space(str(run.space_id), request)
        data = await TestRunService.get_with_results(run_id)
        return data
    except Exception as e:
        logger.error('Unexpected error: %s', e, exc_info=True)
        return None

@mcp.tool()
async def update_test_result(
    result_id: str,
    status: str | None = None,
    comment: str | None = None,
    duration_seconds: int | None = None,
) -> dict:
    """Update test result status and details.

    Args:
        result_id: UUID of the test result
        status: Optional new status: passed | failed | skipped | blocked | not_run
        comment: Optional comment
        duration_seconds: Optional duration in seconds

    Returns:
        Updated result details
    """
    token = get_http_request().headers.get("Authorization", "").replace("Bearer ", "")
    dto = TestResultUpdateDto(
        status=status,
        comment=comment,
        duration_seconds=duration_seconds,
    )
    result = await TestResultService.update_result(
        result_id, dto, token, get_http_request()
    )
    return {
        "id": str(result.id),
        "status": result.status.value if hasattr(result.status, "value") else result.status,
        "comment": result.comment,
        "duration_seconds": result.duration_seconds,
        "executed_at": result.executed_at.isoformat() if result.executed_at else None,
    }

@mcp.tool()
async def link_bug_to_result(result_id: str, bug_short_name: str) -> dict:
    """Link a bug to a test result.

    Args:
        result_id: UUID of the test result
        bug_short_name: Bug identifier (e.g. PROJ-123)

    Returns:
        Updated result with linked bugs
    """
    result = await TestResultModel.get_or_none(id=result_id)
    if not result:
        return {"error": "Result not found"}

    bugs = result.linked_bug_ids or []
    if bug_short_name not in bugs:
        bugs.append(bug_short_name)
        await TestResultModel.filter(id=result_id).update(linked_bug_ids=bugs)

    return {
        "id": str(result.id),
        "linked_bug_ids": bugs,
    }
