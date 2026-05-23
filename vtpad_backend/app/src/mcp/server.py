"""MCP Server for VTPad — exposes test management tools to local AI agents."""

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

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
from ..test_run.service import TestRunService, TestResultService
from ..test_run.dto import TestRunCreateDto, TestResultUpdateDto


class MCPAuthMiddleware(BaseHTTPMiddleware):
    """Verify API Bearer token and attach user_id to request state."""

    async def dispatch(self, request: Request, call_next):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"error": "Missing or invalid Authorization header"}, status_code=401)

        raw_token = auth.replace("Bearer ", "")
        try:
            api_token = await ApiTokenService.validate_token(raw_token)
            request.state.user_id = str(api_token.user_id)
            request.state.api_token_id = str(api_token.id)
            request.state.api_token_scopes = api_token.scopes or []
        except Exception:
            return JSONResponse({"error": "Invalid or expired API token"}, status_code=401)

        return await call_next(request)


mcp = FastMCP("VTPad")


# ─── Helpers ───────────────────────────────────────────────────────────────

def _get_user_id() -> str:
    request = get_http_request()
    return request.state.user_id


def _case_to_dict(case: TestCaseModel) -> dict:
    return {
        "id": str(case.id),
        "title": case.title,
        "type": case.type.value if hasattr(case.type, "value") else case.type,
        "status": case.status.value if hasattr(case.status, "value") else case.status,
        "description": case.text,
        "preconditions": case.preconditions,
        "steps": case.steps,
        "expected_results": case.expected_results,
        "postconditions": case.postconditions,
        "short_name": case.short_name,
        "external_id": case.external_id,
        "space_id": str(case.space_id) if case.space_id else None,
        "suite_id": str(case.suite_id) if case.suite_id else None,
        "section_id": str(case.section_id) if case.section_id else None,
        "sort": case.sort,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
    }


# ─── Tools ───────────────────────────────────────────────────────────────────

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
    except Exception:
        return None


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
            "id": str(s.id),
            "name": s.name,
            "description": s.description,
            "status": s.status.value if hasattr(s.status, "value") else s.status,
            "cases_count": getattr(s, "cases_count", 0),
            "sections_count": getattr(s, "sections_count", 0),
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })
    return items


@mcp.tool()
async def get_tech_doc_tree(space_id: str) -> list[dict]:
    """Get wiki tree of all tech docs in a space.

    Args:
        space_id: UUID of the space

    Returns:
        Hierarchical tree of tech docs
    """
    return await TechDocService.get_tree(space_id)


@mcp.tool()
async def search_tech_docs(
    query: str,
    space_id: str,
    limit: int = 5,
    doc_type: str | None = None,
) -> list[dict]:
    """Search technical documentation by text query.

    Args:
        query: Search string (searches in title and content)
        space_id: UUID of the space
        limit: Maximum results (default 5)
        doc_type: Optional filter: api_doc, prd, manual, wiki, migration, other

    Returns:
        List of matching tech docs
    """
    result = await TechDocService.get_by_space(
        space_id=space_id,
        query=query,
        doc_type=doc_type,
        page=1,
        page_size=limit,
    )
    items = []
    for d in result.get("items", []):
        items.append({
            "id": str(d.id),
            "title": d.title,
            "doc_type": d.doc_type.value if hasattr(d.doc_type, "value") else d.doc_type,
            "source_url": d.source_url,
            "version": d.version,
            "content": d.content[:2000] + "..." if len(d.content) > 2000 else d.content,
        })
    return items


@mcp.tool()
async def semantic_search_tech_docs(
    query: str,
    space_id: str,
    limit: int = 5,
    min_score: float = 0.5,
) -> list[dict]:
    """Semantic search through technical documentation.

    Uses vector embeddings to find docs similar in meaning to the query.

    Args:
        query: Natural language query (e.g. "how does rate limiting work")
        space_id: UUID of the space
        limit: Maximum results (default 5)
        min_score: Minimum similarity threshold (default 0.5)

    Returns:
        List of matching docs with similarity scores
    """
    results = await EmbeddingService.semantic_search(
        space_id=space_id,
        query=query,
        source_types=["tech_doc"],
        top_k=limit,
        min_score=min_score,
    )
    return results


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
    token = get_http_request().headers.get("Authorization", "").replace("Bearer ", "")
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
        data = await TestRunService.get_with_results(run_id)
        return data
    except Exception:
        return None


@mcp.tool()
async def update_test_result(
    result_id: str,
    status: str,
    comment: str | None = None,
    duration_seconds: int | None = None,
) -> dict:
    """Update test result status and details.

    Args:
        result_id: UUID of the test result
        status: New status: passed | failed | skipped | blocked | not_run
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
    result = await TestResultService.update_result(result_id, dto, token)
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
async def get_analytics(space_id: str) -> dict:
    """Get analytics for a space.

    Args:
        space_id: UUID of the space

    Returns:
        Statistics: total cases, runs, pass rate, etc.
    """
    from ..test_case.model import TestCaseModel
    from ..test_suite.model import TestSuiteModel

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
    from ..test_suite.dto import TestSuiteCreateDto
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
async def create_section(
    suite_id: str,
    name: str,
    parent_id: str | None = None,
) -> dict:
    """Create a new section in a test suite.

    Args:
        suite_id: UUID of the test suite
        name: Name of the section
        parent_id: Optional parent section UUID

    Returns:
        Created section details
    """
    from ..section.dto import SectionCreateDto
    from ..section.service import SectionService
    token = get_http_request().headers.get("Authorization", "").replace("Bearer ", "")

    dto = SectionCreateDto(suite_id=suite_id, name=name, parent_id=parent_id)
    section = await SectionService.create(dto, token)
    return {
        "id": str(section.id),
        "name": section.name,
        "suite_id": str(section.suite_id) if section.suite_id else None,
        "parent_id": str(section.parent_id) if section.parent_id else None,
        "sort": section.sort,
    }


# ─── HTTP App for mounting ───────────────────────────────────────────────────

def get_mcp_app():
    """Return the MCP Starlette app with auth middleware."""
    mcp_app = mcp.http_app(path="/mcp")
    mcp_app.add_middleware(MCPAuthMiddleware)
    return mcp_app
