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
async def get_tech_doc_tree(space_id: str) -> list[dict]:
    """Get wiki tree of all tech docs in a space.

    Args:
        space_id: UUID of the space

    Returns:
        Hierarchical tree of tech docs
    """
    return await TechDocService.get_tree(space_id)

@mcp.tool()
async def create_tech_doc(
    space_id: str,
    title: str,
    content: str | None = None,
    doc_type: str = "other",
    source_url: str | None = None,
    version: str | None = None,
    parent_id: str | None = None,
) -> dict:
    """Create a new technical documentation page.

    Args:
        space_id: UUID of the space
        title: Title of the doc
        content: HTML content (Tiptap format)
        doc_type: Type: api_doc, prd, manual, wiki, migration, other
        source_url: Optional source URL
        version: Optional version string
        parent_id: Optional parent doc UUID for nesting

    Returns:
        Created doc details
    """
    from ...tech_doc.dto import TechDocCreateDto

    dto = TechDocCreateDto(
        space_id=space_id,
        title=title,
        content=content,
        doc_type=doc_type,
        source_url=source_url,
        version=version,
        parent_id=parent_id,
    )
    doc = await TechDocService.create(dto)
    return {
        "id": str(doc.id),
        "title": doc.title,
        "doc_type": doc.doc_type.value if hasattr(doc.doc_type, "value") else doc.doc_type,
        "parent_id": str(doc.parent_id) if doc.parent_id else None,
        "sort": doc.sort,
    }

@mcp.tool()
async def update_tech_doc(
    doc_id: str,
    title: str | None = None,
    content: str | None = None,
    doc_type: str | None = None,
    source_url: str | None = None,
    version: str | None = None,
    parent_id: str | None = None,
) -> dict:
    """Update a technical documentation page.

    Args:
        doc_id: UUID of the doc
        title: New title
        content: New HTML content
        doc_type: New type
        source_url: New source URL
        version: New version
        parent_id: New parent UUID (move in tree)

    Returns:
        Updated doc details
    """
    from ...tech_doc.dto import TechDocUpdateDto

    dto = TechDocUpdateDto(
        title=title,
        content=content,
        doc_type=doc_type,
        source_url=source_url,
        version=version,
        parent_id=parent_id,
    )
    doc = await TechDocService.update(doc_id, dto)
    return {
        "id": str(doc.id),
        "title": doc.title,
        "doc_type": doc.doc_type.value if hasattr(doc.doc_type, "value") else doc.doc_type,
        "parent_id": str(doc.parent_id) if doc.parent_id else None,
        "sort": doc.sort,
    }

@mcp.tool()
async def delete_tech_doc(doc_id: str) -> dict:
    """Delete a technical documentation page.

    Cannot delete if page has subpages.

    Args:
        doc_id: UUID of the doc

    Returns:
        Success or error
    """
    try:
        await TechDocService.delete(doc_id)
        return {"deleted": True, "id": doc_id}
    except Exception as e:
        return {"error": str(e)}

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
async def get_doc(doc_id: str) -> dict | None:
    """Get tech doc details by ID.

    Args:
        doc_id: UUID of the tech doc

    Returns:
        Doc details or None
    """
    doc = await TechDocService.get_by_id(doc_id)
    return {
        "id": str(doc.id),
        "title": doc.title,
        "content": doc.content,
        "doc_type": doc.doc_type.value if hasattr(doc.doc_type, "value") else doc.doc_type,
        "source_url": doc.source_url,
        "version": doc.version,
        "parent_id": str(doc.parent_id) if doc.parent_id else None,
        "sort": doc.sort,
    }
