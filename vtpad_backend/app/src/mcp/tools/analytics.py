from datetime import date
from uuid import UUID

from fastapi import HTTPException

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


@mcp.tool()
async def get_analytics(space_id: str) -> dict:
    """Get analytics for a space.

    Args:
        space_id: UUID of the space

    Returns:
        Statistics: total cases, runs, pass rate, etc.
    """
    from ...test_case.model import TestCaseModel
    from ...test_suite.model import TestSuiteModel

    total_cases = await TestCaseModel.filter(space_id=space_id).count()
    active_cases = await TestCaseModel.filter(space_id=space_id, status=TestCaseStatus.active).count()
    total_suites = await TestSuiteModel.filter(space_id=space_id).count()
    total_runs = await TestRunModel.filter(space_id=space_id).count()

    recent_results = await TestResultModel.filter(run__space_id=space_id).order_by("-created_at").limit(100)
    total_recent = len(recent_results)
    passed = sum(1 for r in recent_results if r.status == TestResultStatus.passed)
    failed = sum(1 for r in recent_results if r.status == TestResultStatus.failed)

    pass_rate = round(passed / total_recent * 100, 1) if total_recent else 0

    return {
        "total_cases": total_cases,
        "active_cases": active_cases,
        "total_suites": total_suites,
        "total_runs": total_runs,
        "recent_results_count": total_recent,
        "passed": passed,
        "failed": failed,
        "pass_rate_percent": pass_rate,
    }

@mcp.tool()
async def get_analytics_space(space_id: str) -> dict:
    """Get high-level analytics for a space.

    Args:
        space_id: UUID of the space

    Returns:
        Stats: cases, suites, runs, latest results breakdown
    """
    return await AnalyticsService.get_space_stats(space_id)


def _parse_analytics_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail='dates must use YYYY-MM-DD') from exc


async def _authorize_analytics_request(space_id: str, suite_id: str | None) -> None:
    try:
        UUID(space_id)
    except (TypeError, ValueError, AttributeError) as exc:
        raise HTTPException(status_code=422, detail='space_id must be a UUID') from exc
    AnalyticsService._validate_suite_filter(suite_id)
    request = get_http_request()
    await check_user_into_space(space_id, request)
    if suite_id is not None and not await TestSuiteModel.filter(id=suite_id, space_id=space_id).exists():
        raise HTTPException(status_code=404, detail='not found')


@mcp.tool()
async def get_quality_trends(
    space_id: str,
    suite_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """Get weekly failed rates and recurrent failures for a space or suite.

    Dates are inclusive UTC calendar dates in YYYY-MM-DD format. With no dates,
    the service uses the latest twelve complete Monday-to-Sunday weeks.
    """
    await _authorize_analytics_request(space_id, suite_id)
    return await AnalyticsService.get_quality_trends(
        space_id, suite_id, _parse_analytics_date(start_date), _parse_analytics_date(end_date)
    )


@mcp.tool()
async def get_quality_results(
    space_id: str,
    suite_id: str,
    week_start: str,
    status: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> dict:
    """Get a paginated source-result drill-down for one UTC Monday week.

    Returned run/result IDs are the rows contributing to the suite's failed-rate
    denominator. `not_run` results are excluded, matching the aggregate.
    """
    await _authorize_analytics_request(space_id, suite_id)
    parsed_week_start = _parse_analytics_date(week_start)
    if parsed_week_start is None:
        raise HTTPException(status_code=422, detail='week_start is required')
    return await AnalyticsService.get_quality_results(
        space_id, suite_id, parsed_week_start, page, page_size, status
    )


@mcp.tool()
async def get_time_trends(
    space_id: str,
    suite_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """Get estimated, measured case and active run time for completed runs.

    Dates are inclusive UTC calendar dates in YYYY-MM-DD format. Ranges up to
    31 days use daily buckets; longer ranges use Monday-based UTC weeks.
    """
    await _authorize_analytics_request(space_id, suite_id)
    return await AnalyticsService.get_time_trends(
        space_id, suite_id, _parse_analytics_date(start_date), _parse_analytics_date(end_date)
    )
