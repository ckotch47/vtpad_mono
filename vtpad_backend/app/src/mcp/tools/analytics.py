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
