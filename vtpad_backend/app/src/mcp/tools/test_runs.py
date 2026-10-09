import uuid

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
from ...test_run.model import TestRunModel
from ...space.model import SpaceModel
from ...test_run.service import TestRunService, TestResultService
from ...test_run.dto import (
    TestRunCreateDto, TestResultUpdateDto, TestResultBugCreateDto,
)
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
async def compare_test_runs(run_id: str, other_run_id: str) -> dict:
    """Compare two completed test runs from the same space using their snapshots.

    Args:
        run_id: UUID of the first completed test run
        other_run_id: UUID of the second completed test run

    Returns:
        Snapshot-based case and result differences
    """
    return await TestRunService.compare_runs(run_id, other_run_id, get_http_request())

@mcp.tool()
async def update_test_result(
    result_id: str,
    status: str | None = None,
    comment: str | None = None,
    duration_seconds: int | None = None,
    linked_bug_ids: list[str] | None = None,
    clear_legacy_linked_bug_ids: bool = False,
) -> dict:
    """Update test result status and details.

    Args:
        result_id: UUID of the test result
        status: Optional new status: passed | failed | skipped | blocked | not_run
        comment: Optional comment
        duration_seconds: Optional duration in seconds
        linked_bug_ids: Optional legacy short-name values; does not change UUID links
        clear_legacy_linked_bug_ids: Set the legacy JSON field to null

    Returns:
        Updated result details
    """
    token = get_http_request().headers.get("Authorization", "").replace("Bearer ", "")
    dto_data = dict(
        status=status,
        comment=comment,
        duration_seconds=duration_seconds,
    )
    if linked_bug_ids is not None:
        dto_data["linked_bug_ids"] = linked_bug_ids
    elif clear_legacy_linked_bug_ids:
        dto_data["linked_bug_ids"] = None
    dto = TestResultUpdateDto(**dto_data)
    result = await TestResultService.update_result(
        result_id, dto, token, get_http_request()
    )
    return result

@mcp.tool()
async def link_bug_to_result(result_id: str, bug_short_name: str) -> dict:
    """Append an unambiguous same-space short name to legacy JSON references.

    Args:
        result_id: UUID of the test result
        bug_short_name: Bug identifier (e.g. PROJ-123)

    Returns:
        Updated legacy linked_bug_ids array; use UUID tools for new links
    """
    return await TestResultService.update_legacy_bug_reference(
        result_id, bug_short_name, get_http_request(), add=True
    )


@mcp.tool()
async def unlink_bug_from_result(result_id: str, bug_short_name: str) -> dict:
    """Remove an unambiguous same-space short name from legacy JSON references."""
    return await TestResultService.update_legacy_bug_reference(
        result_id, bug_short_name, get_http_request(), add=False
    )


@mcp.tool()
async def link_bug_uuid_to_result(result_id: str, bug_uuid: uuid.UUID) -> dict:
    """Link a same-space bug to an active result using its UUID."""
    return await TestResultService.link_bug_id(result_id, bug_uuid, get_http_request())


@mcp.tool()
async def unlink_bug_uuid_from_result(result_id: str, bug_uuid: uuid.UUID) -> dict:
    """Unlink a same-space bug from an active result using its UUID."""
    return await TestResultService.unlink_bug_id(result_id, bug_uuid, get_http_request())


@mcp.tool()
async def create_and_link_bug_to_result(
    result_id: str,
    operation_id: uuid.UUID,
    title: str,
    text: str | None = None,
    steps: str | None = None,
) -> dict:
    """Atomically create a bug and link it to a result; reuse operation_id on retry."""
    request = get_http_request()
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    dto = TestResultBugCreateDto(
        operation_id=operation_id,
        title=title,
        text=text,
        steps=steps,
    )
    return await TestResultService.create_and_link_bug(
        result_id, dto, token, request
    )
