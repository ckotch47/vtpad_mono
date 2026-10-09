from uuid import UUID

from fastapi import HTTPException
from fastmcp.server.dependencies import get_http_request

from ..core import mcp
from ...common.right_guard import check_user_into_space
from ...tag.dto import CreateTagDto, UpdateTagDto
from ...tag.model import TagModel
from ...tag.service import TagService


async def _require_space_access(space_id: str, capability: str | None = None) -> None:
    await check_user_into_space(space_id, get_http_request(), capability=capability)


async def _require_tag_access(tag_id: str, capability: str | None = None) -> TagModel:
    tag = await TagModel.get_or_none(id=tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    await _require_space_access(str(tag.space_id), capability)
    return tag


def _serialize_tag(tag: TagModel) -> dict:
    return {
        "id": str(tag.id),
        "title": tag.title,
        "color": tag.color,
        "create_date": tag.create_date.isoformat() if tag.create_date else None,
        "space_id": str(tag.space_id),
    }


@mcp.tool()
async def list_tags(space_id: UUID) -> list[dict]:
    """List the shared Space tags used by Bugs and test cases."""
    await _require_space_access(str(space_id))
    tags = await TagModel.filter(space_id=str(space_id)).order_by("create_date", "id")
    return [_serialize_tag(tag) for tag in tags]


@mcp.tool()
async def create_tag(space_id: UUID, title: str, color: str | None = None) -> dict:
    """Create or reuse a normalized shared Space tag."""
    await _require_space_access(str(space_id), "tags")
    tag = await TagService.create_tag(str(space_id), CreateTagDto(title=title, color=color))
    return _serialize_tag(tag)


@mcp.tool()
async def update_tag(tag_id: UUID, title: str, color: str | None = None) -> dict:
    """Rename or recolor a shared Space tag."""
    await _require_tag_access(str(tag_id), "tags")
    tag = await TagService.update_tag(str(tag_id), UpdateTagDto(title=title, color=color))
    return _serialize_tag(tag)


@mcp.tool()
async def delete_tag(tag_id: UUID) -> bool:
    """Delete a shared Space tag and its current Bug/test-case associations."""
    await _require_tag_access(str(tag_id), "tags")
    return await TagService.delete_tag(str(tag_id))
