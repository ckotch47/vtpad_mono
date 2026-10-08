# MCP integration

## Endpoint and authentication

The FastMCP HTTP application is mounted by the backend at `/v1/mcp` (JSON-RPC over HTTP/SSE). MCP requests use `Authorization: Bearer <API token>`. `MCPAuthMiddleware` validates the token and records the authenticated user in request state; shared space guards use that identity for authorization.

## Section ordering

The `sort_sections` tool reorders one section within its current sibling group. Supply `section_id` and exactly one of `sort_before_id` or `sort_after_id`. The target and neighbor must share both suite and parent. The tool calls the same `SectionService.update_sort` implementation as REST, which derives the space from the target's suite, checks the user's membership, and updates sibling positions transactionally.

The result is a JSON array of siblings ordered by `sort`, with `id`, `name`, `description`, `suite_id`, `parent_id`, and `sort`. A membership failure is surfaced as an MCP tool error. Invalid neighbor combinations and non-sibling references are rejected by the shared DTO/service validation.

## Registration

MCP tools are registered through imports in `app/src/mcp/tools/__init__.py`; section tools live in `app/src/mcp/tools/sections.py`. The HTTP application and authentication middleware are defined in `app/src/mcp/server.py` and `app/src/mcp/middleware.py`.
