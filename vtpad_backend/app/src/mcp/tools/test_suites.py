from ..core import mcp
from ..utils import _get_user_id, _case_to_dict
from fastmcp.server.dependencies import get_http_request

from ...api_token.service import ApiTokenService
from ...test_case.model import TestCaseModel, TestCaseStatus, TestCaseType
from ...test_case.service import TestCaseService
from .test_cases import _delete_case_cascade, _delete_run_cascade
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
async def get_suite_tree(suite_id: str) -> dict | None:
    """Get full tree of a test suite: suite info + sections + test cases.

    Args:
        suite_id: UUID of the test suite

    Returns:
        Suite tree with nested sections and cases
    """
    try:
        suite = await TestSuiteService.get_by_id(suite_id)
        sections = await SectionModel.filter(suite_id=suite_id).order_by("sort").all()
        cases = await TestCaseService.get_by_suite(suite_id)

        # Build section tree
        section_map = {}
        for s in sections:
            section_map[str(s.id)] = {
                "id": str(s.id),
                "name": s.name,
                "sort": s.sort,
                "parent_id": str(s.parent_id) if s.parent_id else None,
                "cases": [],
                "children": [],
            }

        # Attach cases to sections
        for c in cases:
            sid = str(c.section_id) if c.section_id else None
            if sid and sid in section_map:
                section_map[sid]["cases"].append(_case_to_dict(c))

        # Build hierarchy
        root_sections = []
        for s in section_map.values():
            pid = s["parent_id"]
            if pid and pid in section_map:
                section_map[pid]["children"].append(s)
            else:
                root_sections.append(s)

        return {
            "id": str(suite.id),
            "name": suite.name,
            "description": suite.description,
            "status": suite.status.value if hasattr(suite.status, "value") else suite.status,
            "space_id": str(suite.space_id) if suite.space_id else None,
            "sections": root_sections,
            "uncategorized_cases": [_case_to_dict(c) for c in cases if not c.section_id],
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_space_suites(space_id: str, limit: int = 25) -> list[dict]:
    """List test suites in a space.

    Args:
        space_id: UUID of the space
        limit: Maximum number of results

    Returns:
        List of test suites
    """
    result = await TestSuiteService.get_by_space(
        space_id=space_id,
        page=1,
        page_size=limit,
    )
    items = []
    for s in result.get("items", []):
        items.append({
            "id": str(s.get("id")),
            "name": s.get("name"),
            "description": s.get("description"),
            "status": s.get("status"),
            "cases_count": s.get("cases_count", 0),
            "sections_count": s.get("sections_count", 0),
            "created_at": s.get("created_at"),
        })
    return items

@mcp.tool()
async def create_suite(
    space_id: str,
    name: str,
    description: str | None = None,
) -> dict:
    """Create a new test suite.

    Args:
        space_id: UUID of the space
        name: Name of the suite
        description: Optional description

    Returns:
        Created suite details
    """
    from ...test_suite.dto import TestSuiteCreateDto
    token = get_http_request().headers.get("Authorization", "").replace("Bearer ", "")

    dto = TestSuiteCreateDto(space_id=space_id, name=name, description=description)
    suite = await TestSuiteService.create(dto, token)
    return {
        "id": str(suite.id),
        "name": suite.name,
        "description": suite.description,
        "space_id": str(suite.space_id) if suite.space_id else None,
    }

@mcp.tool()
async def update_suite(
    suite_id: str,
    name: str | None = None,
    description: str | None = None,
    status: str | None = None,
) -> dict:
    """Update a test suite.

    Args:
        suite_id: UUID of the test suite
        name: New name
        description: New description
        status: New status: active | archived

    Returns:
        Updated suite details
    """
    dto = TestSuiteUpdateDto(
        name=name,
        description=description,
        status=status,
    )
    suite = await TestSuiteService.update(suite_id, dto)
    return {
        "id": str(suite.id),
        "name": suite.name,
        "description": suite.description,
        "status": suite.status.value if hasattr(suite.status, "value") else suite.status,
        "space_id": str(suite.space_id) if suite.space_id else None,
    }

@mcp.tool()
async def delete_suite(suite_id: str) -> dict:
    """Delete (archive) a test suite.

    Args:
        suite_id: UUID of the test suite

    Returns:
        Success status
    """
    await TestSuiteService.delete(suite_id)
    return {"deleted": True, "id": suite_id}

@mcp.tool()
async def hard_delete_suite(suite_id: str) -> dict:
    """Permanently delete a suite and all related sections/cases/runs/embeddings.

    WARNING: This cannot be undone. Use with extreme caution.

    Args:
        suite_id: UUID of the test suite

    Returns:
        Success status
    """
    cases = await TestCaseModel.filter(suite_id=suite_id).all()
    for case in cases:
        await _delete_case_cascade(str(case.id))
    runs = await TestRunModel.filter(suite_id=suite_id).all()
    for run in runs:
        await _delete_run_cascade(str(run.id))
    await SectionModel.filter(suite_id=suite_id).delete()
    await EmbeddingService.delete_embeddings('test_suite', suite_id)
    await TestSuiteModel.filter(id=suite_id).delete()
    return {"hard_deleted": True, "id": suite_id}

@mcp.tool()
async def get_analytics_coverage(suite_id: str) -> dict:
    """Get coverage breakdown for a suite (manual/automated/checklist percentages).

    Args:
        suite_id: UUID of the test suite

    Returns:
        Coverage stats with counts and percentages
    """
    return await AnalyticsService.get_suite_coverage(suite_id)


# ─── HTTP App for mounting ───────────────────────────────────────────────────

def get_mcp_app():
    """Return the MCP Starlette app with auth middleware."""
    mcp_app = mcp.http_app(path="/mcp")
    mcp_app.add_middleware(MCPAuthMiddleware)
    return mcp_app
