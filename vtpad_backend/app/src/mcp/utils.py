"""MCP tool utilities."""

from fastmcp.server.dependencies import get_http_request
from ..test_case.model import TestCaseModel


def _get_user_id() -> str:
    request = get_http_request()
    return request.state.user_id


def _case_to_dict(case: TestCaseModel) -> dict:
    value = case.get if isinstance(case, dict) else lambda key: getattr(case, key, None)
    case_type = value('type')
    case_status = value('status')
    space_id = value('space_id')
    suite_id = value('suite_id')
    section_id = value('section_id')
    created_at = value('created_at')
    updated_at = value('updated_at')
    return {
        "id": str(value('id')),
        "title": value('title'),
        "type": case_type.value if hasattr(case_type, "value") else case_type,
        "status": case_status.value if hasattr(case_status, "value") else case_status,
        "description": value('text'),
        "preconditions": value('preconditions'),
        "steps": value('steps'),
        "expected_results": value('expected_results'),
        "postconditions": value('postconditions'),
        "estimated_duration_seconds": value('estimated_duration_seconds'),
        "short_name": value('short_name'),
        "external_id": value('external_id'),
        "space_id": str(space_id) if space_id else None,
        "suite_id": str(suite_id) if suite_id else None,
        "section_id": str(section_id) if section_id else None,
        "sort": value('sort'),
        "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else created_at,
        "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else updated_at,
    }
