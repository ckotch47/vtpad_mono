"""MCP tools for the versioned space content exchange API."""

from fastmcp.server.dependencies import get_http_request

from ..core import mcp
from ...data_exchange.service import export_content, import_content, preview_import


@mcp.tool()
async def export_space_data(
    space_id: str,
    format: str = "json",
    suite_ids: list[str] | None = None,
) -> dict:
    """Export suites, sections, test cases, tags and typed custom fields."""
    return await export_content(space_id, format, get_http_request(), suite_ids)


@mcp.tool()
async def preview_space_import(space_id: str, content: str, format: str = "json") -> dict:
    """Validate a JSON or CSV import and return an escaped, bounded preview."""
    return await preview_import(space_id, format, content.encode("utf-8"), get_http_request())


@mcp.tool()
async def import_space_data(
    space_id: str,
    content: str,
    idempotency_key: str,
    format: str = "json",
) -> dict:
    """Atomically import JSON or CSV content using a caller-supplied idempotency key."""
    return await import_content(
        space_id, format, content.encode("utf-8"), idempotency_key, get_http_request()
    )
