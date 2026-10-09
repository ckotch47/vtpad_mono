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
        "priority": value('priority'),
        "tags": value('tags'),
        "custom_fields": value('custom_fields'),
        "short_name": value('short_name'),
        "external_id": value('external_id'),
        "space_id": str(space_id) if space_id else None,
        "suite_id": str(suite_id) if suite_id else None,
        "section_id": str(section_id) if section_id else None,
        "sort": value('sort'),
        "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else created_at,
        "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else updated_at,
    }


async def _cases_to_dict_with_metadata(cases: list[TestCaseModel]) -> list[dict]:
    """Serialize a collection of cases and fetch tag relations in one batch."""
    values = [_case_to_dict(case) for case in cases]
    missing_tag_ids = [value["id"] for value in values if value.get("tags") is None]
    if missing_tag_ids:
        from ..test_case.service import TestCaseService
        tags_by_case = await TestCaseService.get_tags_for_cases(missing_tag_ids)
        for value in values:
            if value.get("tags") is None:
                value["tags"] = tags_by_case.get(value["id"], [])
    missing_custom_field_ids = [value["id"] for value in values if value.get("custom_fields") is None]
    if missing_custom_field_ids:
        from ..custom_field.service import CustomFieldValueService
        custom_fields_by_case: dict[str, list[dict]] = {}
        cases_by_space: dict[str, list[str]] = {}
        for case in cases:
            case_id = str(case.id)
            if case_id in missing_custom_field_ids:
                cases_by_space.setdefault(str(case.space_id), []).append(case_id)
        for space_id, case_ids in cases_by_space.items():
            custom_fields_by_case.update(
                await CustomFieldValueService.get_snapshot_values(space_id, case_ids)
            )
        for value in values:
            if value.get("custom_fields") is None:
                value["custom_fields"] = custom_fields_by_case.get(value["id"], [])
    return values
