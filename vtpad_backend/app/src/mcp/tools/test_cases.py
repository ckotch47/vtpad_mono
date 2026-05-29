from ..core import mcp
from ..utils import _get_user_id, _case_to_dict
from fastmcp.server.dependencies import get_http_request

from ..api_token.service import ApiTokenService
from ..test_case.model import TestCaseModel, TestCaseStatus, TestCaseType
from ..test_case.service import TestCaseService
from ..test_suite.model import TestSuiteModel
from ..test_suite.service import TestSuiteService
from ..section.model import SectionModel
from ..section.service import SectionService
from ..embedding.service import EmbeddingService
from ..tech_doc.model import TechDocModel
from ..tech_doc.service import TechDocService
from ..test_run.model import TestRunModel, TestResultModel, TestRunStatus, TestResultStatus
from ..space.model import SpaceModel
from ..test_run.service import TestRunService, TestResultService
from ..test_run.dto import TestRunCreateDto, TestResultUpdateDto
from ..test_case.dto import TestCaseUpdateDto
from ..test_suite.dto import TestSuiteUpdateDto
from ..section.dto import SectionUpdateDto
from ..test_plan.model import TestPlanModel
from ..test_plan.service import TestPlanService
from ..analytics.service import AnalyticsService
import logging
logger = logging.getLogger(__name__)


@mcp.tool()
async def search_test_cases(
    query: str,
    space_id: str,
    limit: int = 10,
    type_filter: str | None = None,
    status_filter: str | None = None,
) -> list[dict]:
    """Search test cases by text query (title, short_name) in a space.

    Args:
        query: Search string (searches in title and short_name)
        space_id: UUID of the space to search in
        limit: Maximum number of results (default 10)
        type_filter: Optional filter by type: manual | automated | checklist
        status_filter: Optional filter by status: draft | active | deprecated

    Returns:
        List of test cases matching the query
    """
    result = await TestCaseService.get_by_space(
        space_id=space_id,
        type_filter=type_filter,
        status_filter=status_filter,
        page=1,
        page_size=limit,
        search=query,
        sort_by="created_at",
        sort_order="desc",
    )
    return [_case_to_dict(c) for c in result.get("items", [])]

@mcp.tool()
async def get_test_case(case_id: str) -> dict | None:
    """Get full details of a test case by ID.

    Args:
        case_id: UUID of the test case

    Returns:
        Test case details or None if not found
    """
    try:
        case = await TestCaseService.get_by_id(case_id)
        return _case_to_dict(case)
    except Exception as e:
        logger.error('Unexpected error: %s', e, exc_info=True)
        return None

@mcp.tool()
async def create_test_case(
    space_id: str,
    suite_id: str,
    title: str,
    type: str = "manual",
    section_id: str | None = None,
    description: str | None = None,
    preconditions: str | None = None,
    steps: str | None = None,
    expected_results: str | None = None,
    postconditions: str | None = None,
    short_name: str | None = None,
    external_id: str | None = None,
) -> dict:
    """Create a new test case.

    Args:
        space_id: UUID of the space
        suite_id: UUID of the test suite
        title: Title of the test case
        type: Type of test case: manual | automated | checklist (default: manual)
        section_id: Optional UUID of the section
        description: Optional description (HTML or text)
        preconditions: Optional preconditions
        steps: Optional test steps
        expected_results: Optional expected results
        postconditions: Optional postconditions
        short_name: Optional short identifier
        external_id: Optional external ID (for automated tests)

    Returns:
        Created test case details
    """
    from ..test_case.dto import TestCaseCreateDto

    token = get_http_request().headers.get("Authorization", "").replace("Bearer ", "")

    dto = TestCaseCreateDto(
        space_id=space_id,
        suite_id=suite_id,
        section_id=section_id,
        title=title,
        type=type,
        text=description,
        preconditions=preconditions,
        steps=steps,
        expected_results=expected_results,
        postconditions=postconditions,
        short_name=short_name,
        external_id=external_id,
    )
    case = await TestCaseService.create(dto, token)
    return _case_to_dict(case)

@mcp.tool()
async def update_test_case(
    case_id: str,
    title: str | None = None,
    description: str | None = None,
    preconditions: str | None = None,
    steps: str | None = None,
    expected_results: str | None = None,
    postconditions: str | None = None,
    type: str | None = None,
    status: str | None = None,
    section_id: str | None = None,
    suite_id: str | None = None,
    short_name: str | None = None,
    external_id: str | None = None,
) -> dict:
    """Update a test case.

    Args:
        case_id: UUID of the test case
        title: New title
        description: New description
        preconditions: New preconditions
        steps: New test steps
        expected_results: New expected results
        postconditions: New postconditions
        type: New type: manual | automated | checklist
        status: New status: draft | active | deprecated
        section_id: New section UUID
        suite_id: New suite UUID
        short_name: New short identifier
        external_id: New external ID

    Returns:
        Updated test case details
    """
    dto = TestCaseUpdateDto(
        title=title,
        text=description,
        preconditions=preconditions,
        steps=steps,
        expected_results=expected_results,
        postconditions=postconditions,
        type=type,
        status=status,
        section_id=section_id,
        suite_id=suite_id,
        short_name=short_name,
        external_id=external_id,
    )
    case = await TestCaseService.update(case_id, dto)
    return _case_to_dict(case)

@mcp.tool()
async def delete_test_case(case_id: str) -> dict:
    """Delete a test case permanently.

    Args:
        case_id: UUID of the test case

    Returns:
        Success status
    """
    await TestCaseService.delete(case_id)
    return {"deleted": True, "id": case_id}

@mcp.tool()
async def hard_delete_test_case(case_id: str) -> dict:
    """Permanently delete a test case and all related results/step-results/embeddings.

    WARNING: This cannot be undone.

    Args:
        case_id: UUID of the test case

    Returns:
        Success status
    """
    await _delete_case_cascade(case_id)
    return {"hard_deleted": True, "id": case_id}

@mcp.tool()
async def duplicate_test_case(case_id: str) -> dict:
    """Duplicate a test case.

    Creates a copy with '(Copy)' suffix in title.

    Args:
        case_id: UUID of the test case to duplicate

    Returns:
        Duplicated test case
    """
    token = _get_user_id()
    case = await TestCaseService.duplicate(case_id, token)
    return _case_to_dict(case)

@mcp.tool()
async def move_test_case(
    case_id: str,
    suite_id: str | None = None,
    section_id: str | None = None,
) -> dict:
    """Move a test case to another suite or section.

    Args:
        case_id: UUID of the test case
        suite_id: Optional new suite UUID
        section_id: Optional new section UUID

    Returns:
        Updated test case
    """
    dto = TestCaseUpdateDto(suite_id=suite_id, section_id=section_id)
    case = await TestCaseService.update(case_id, dto)
    return _case_to_dict(case)


async def _delete_case_cascade(case_id: str) -> None:
    """Delete a test case and all related results, step results, and embeddings."""
    await EmbeddingService.delete_embeddings('test_case', case_id)
    results = await TestResultModel.filter(testcase_id=case_id).all()
    result_ids = [str(r.id) for r in results]
    if result_ids:
        await TestResultModel.filter(id__in=result_ids).delete()
    await TestCaseModel.filter(id=case_id).delete()


async def _delete_run_cascade(run_id: str) -> None:
    """Delete a test run and all related results and step results."""
    results = await TestResultModel.filter(run_id=run_id).all()
    result_ids = [str(r.id) for r in results]
    if result_ids:
        await TestResultModel.filter(id__in=result_ids).delete()
    await TestRunModel.filter(id=run_id).delete()

@mcp.tool()
async def get_case_history(case_id: str, limit: int = 20) -> list[dict]:
    """Get execution history of a test case.

    Args:
        case_id: UUID of the test case
        limit: Maximum number of results (default 20)

    Returns:
        List of test results for this case
    """
    results = await TestResultModel.filter(testcase_id=case_id).prefetch_related("run").order_by("-created_at").limit(limit)
    items = []
    for r in results:
        items.append({
            "id": str(r.id),
            "run_id": str(r.run_id),
            "run_name": r.run.name if r.run else None,
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "duration_seconds": r.duration_seconds,
            "comment": r.comment,
            "executed_at": r.executed_at.isoformat() if r.executed_at else None,
        })
    return items

@mcp.tool()
async def find_similar_cases(
    case_id: str,
    limit: int = 5,
    min_score: float = 0.75,
) -> list[dict]:
    """Find test cases semantically similar to a given case.

    Args:
        case_id: UUID of the reference test case
        limit: Maximum number of similar cases (default 5)
        min_score: Minimum similarity threshold (default 0.75)

    Returns:
        List of similar cases with similarity scores
    """
    case = await TestCaseService.get_by_id(case_id)
    space_id = str(case.space_id)

    # Build query from case content
    query = f"{case.title}\n{case.text or ''}\n{case.steps or ''}"
    results = await EmbeddingService.semantic_search(
        space_id=space_id,
        query=query,
        source_types=["test_case"],
        top_k=limit + 1,  # +1 because the case itself will match
        min_score=min_score,
    )
    # Exclude the reference case itself
    return [r for r in results if r["source_id"] != case_id][:limit]

@mcp.tool()
async def semantic_search_cases(
    query: str,
    space_id: str,
    limit: int = 10,
    min_score: float = 0.5,
) -> list[dict]:
    """Semantic search test cases by natural language query.

    Uses vector embeddings to find cases similar in meaning to the query,
    not just text matching. Requires OPENAI_API_KEY to be configured.

    Args:
        query: Natural language query (e.g. "how to test OAuth2 login")
        space_id: UUID of the space to search in
        limit: Maximum results (default 10)
        min_score: Minimum similarity threshold 0-1 (default 0.7)

    Returns:
        List of matching cases with similarity scores
    """
    results = await EmbeddingService.semantic_search(
        space_id=space_id,
        query=query,
        source_types=["test_case"],
        top_k=limit,
        min_score=min_score,
    )
    return results
