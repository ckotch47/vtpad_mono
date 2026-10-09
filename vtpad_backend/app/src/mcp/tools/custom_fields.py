"""MCP access to space-scoped custom fields using shared REST services."""

from typing import Any

from fastmcp.server.dependencies import get_http_request

from ..core import mcp
from ...custom_field.dto import (
    CustomFieldCreateDto,
    CustomFieldUpdateDto,
    CustomFieldValueDto,
)
from ...custom_field.service import CustomFieldService, CustomFieldValueService


def _request_and_token():
    request = get_http_request()
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    return request, token


def _field_to_dict(field) -> dict:
    return {
        'id': str(field.id),
        'name': field.name,
        'field_type': field.field_type.value if hasattr(field.field_type, 'value') else field.field_type,
        'entity_type': field.entity_type.value if hasattr(field.entity_type, 'value') else field.entity_type,
        'options': field.options or [],
        'required': bool(field.required),
        'sort': field.sort,
        'space_id': str(field.space_id),
    }


@mcp.tool()
async def list_custom_fields(space_id: str, entity_type: str = 'testcase') -> list[dict]:
    """List custom field definitions in a space (testcase or testrun)."""
    request, _token = _request_and_token()
    fields = await CustomFieldService.get_by_space(space_id, entity_type, request)
    return [_field_to_dict(field) for field in fields]


@mcp.tool()
async def create_custom_field(
    space_id: str,
    name: str,
    field_type: str,
    entity_type: str = 'testcase',
    options: list[str] | None = None,
    required: bool = False,
    sort: int = 0,
) -> dict:
    """Create a typed, space-scoped custom field definition."""
    request, token = _request_and_token()
    field = await CustomFieldService.create(CustomFieldCreateDto(
        space_id=space_id,
        name=name,
        field_type=field_type,
        entity_type=entity_type,
        options=options,
        required=required,
        sort=sort,
    ), token, request)
    return _field_to_dict(field)


@mcp.tool()
async def update_custom_field(
    field_id: str,
    name: str | None = None,
    field_type: str | None = None,
    options: list[str] | None = None,
    required: bool | None = None,
    sort: int | None = None,
) -> dict:
    """Update a field definition; incompatible existing values are rejected."""
    request, _token = _request_and_token()
    values = {
        'name': name,
        'field_type': field_type,
        'options': options,
        'required': required,
        'sort': sort,
    }
    dto = CustomFieldUpdateDto(**{key: value for key, value in values.items() if value is not None})
    field = await CustomFieldService.update(field_id, dto, request)
    return _field_to_dict(field)


@mcp.tool()
async def delete_custom_field(field_id: str) -> dict:
    """Delete a field definition and its live values; snapshots remain intact."""
    request, _token = _request_and_token()
    await CustomFieldService.delete(field_id, request)
    return {'deleted': True, 'id': field_id}


@mcp.tool()
async def set_custom_field_value(field_id: str, entity_id: str, value: Any) -> dict:
    """Set one custom field value after type, entity-space, and access validation."""
    request, _token = _request_and_token()
    saved = await CustomFieldValueService.set_value(
        CustomFieldValueDto(field_id=field_id, entity_id=entity_id, value=value), request, _token
    )
    return {
        'id': str(saved.id),
        'field_id': str(saved.field_id),
        'entity_id': str(saved.entity_id),
        'value': saved.value,
    }


@mcp.tool()
async def get_custom_field_values(entity_id: str) -> list[dict]:
    """Get validated custom field values for an authorized entity."""
    request, _token = _request_and_token()
    values = await CustomFieldValueService.get_values(entity_id, request)
    return [
        {
            'id': str(value.id),
            'field_id': str(value.field_id),
            'entity_id': str(value.entity_id),
            'value': value.value,
            'field': _field_to_dict(value.field),
        }
        for value in values
    ]
