"""MCP tool utilities."""

from fastmcp.server.dependencies import get_http_request
from ..test_case.model import TestCaseModel


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
