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
from ...section.dto import SectionSortDto, SectionUpdateDto
from ...test_plan.model import TestPlanModel
from ...test_plan.service import TestPlanService
from ...analytics.service import AnalyticsService
from ...common.right_guard import check_user_into_space
import logging
logger = logging.getLogger(__name__)


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
    from ...section.dto import SectionCreateDto
    from ...section.service import SectionService
    request = get_http_request()
    suite = await TestSuiteService.get_by_id(suite_id)
    await check_user_into_space(str(suite.space_id), request, capability="sections")
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    dto = SectionCreateDto(suite_id=suite_id, name=name, parent_id=parent_id)
    section = await SectionService.create(dto, token)
    return {
        "id": str(section.id),
        "name": section.name,
        "suite_id": str(section.suite_id) if section.suite_id else None,
        "parent_id": str(section.parent_id) if section.parent_id else None,
        "sort": section.sort,
    }

@mcp.tool()
async def update_section(
    section_id: str,
    name: str | None = None,
    description: str | None = None,
    parent_id: str | None = None,
) -> dict:
    """Update a section in a test suite.

    Args:
        section_id: UUID of the section
        name: New name
        description: New description
        parent_id: New parent section UUID

    Returns:
        Updated section details
    """
    section = await SectionService.get_by_id(section_id)
    suite = await TestSuiteService.get_by_id(str(section.suite_id))
    await check_user_into_space(str(suite.space_id), get_http_request(), capability="sections")
    dto = SectionUpdateDto(
        name=name,
        description=description,
        parent_id=parent_id,
    )
    section = await SectionService.update(section_id, dto)
    return {
        "id": str(section.id),
        "name": section.name,
        "suite_id": str(section.suite_id) if section.suite_id else None,
        "parent_id": str(section.parent_id) if section.parent_id else None,
        "sort": section.sort,
    }

@mcp.tool()
async def delete_section(section_id: str) -> dict:
    """Delete a section.

    Args:
        section_id: UUID of the section

    Returns:
        Success status
    """
    section = await SectionService.get_by_id(section_id)
    suite = await TestSuiteService.get_by_id(str(section.suite_id))
    await check_user_into_space(str(suite.space_id), get_http_request(), capability="sections")
    await SectionService.delete(section_id)
    return {"deleted": True, "id": section_id}

@mcp.tool()
async def sort_sections(
    section_id: str,
    sort_before_id: str | None = None,
    sort_after_id: str | None = None,
) -> list[dict]:
    """Move a section before or after one of its siblings.

    Exactly one of sort_before_id and sort_after_id must be provided. Sections
    can only be reordered within the same test suite and parent section.

    Args:
        section_id: UUID of the section to move
        sort_before_id: Optional UUID of a sibling to place this section before
        sort_after_id: Optional UUID of a sibling to place this section after

    Returns:
        The updated ordered siblings, including their parent and suite IDs
    """
    dto = SectionSortDto(
        sort_before_id=sort_before_id,
        sort_after_id=sort_after_id,
    )
    siblings = await SectionService.update_sort(
        section_id,
        dto,
        get_http_request(),
    )
    return [
        {
            "id": str(section.id),
            "name": section.name,
            "description": section.description,
            "suite_id": str(section.suite_id) if section.suite_id else None,
            "parent_id": str(section.parent_id) if section.parent_id else None,
            "sort": section.sort,
        }
        for section in siblings
    ]

@mcp.tool()
async def hard_delete_section(section_id: str) -> dict:
    """Permanently delete a section. Cases in this section will have section_id set to null.

    Args:
        section_id: UUID of the section

    Returns:
        Success status
    """
    section = await SectionService.get_by_id(section_id)
    suite = await TestSuiteService.get_by_id(str(section.suite_id))
    await check_user_into_space(str(suite.space_id), get_http_request(), capability="sections")
    await TestCaseModel.filter(section_id=section_id).update(section_id=None)
    await EmbeddingService.delete_embeddings('section', section_id)
    await SectionModel.filter(id=section_id).delete()
    return {"hard_deleted": True, "id": section_id}


# ─── Test Plan Tools ──────────────────────────────────────────────────────────

@mcp.tool()
async def get_section(section_id: str) -> dict | None:
    """Get section details by ID.

    Args:
        section_id: UUID of the section

    Returns:
        Section details or None
    """
    section = await SectionModel.get_or_none(id=section_id)
    if not section:
        return None
    suite = await TestSuiteService.get_by_id(str(section.suite_id))
    await check_user_into_space(str(suite.space_id), get_http_request())
    return {
        "id": str(section.id),
        "name": section.name,
        "description": section.description,
        "suite_id": str(section.suite_id) if section.suite_id else None,
        "parent_id": str(section.parent_id) if section.parent_id else None,
        "sort": section.sort,
    }
