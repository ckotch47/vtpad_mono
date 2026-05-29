"""MCP Server for VTPad — exposes test management tools to local AI agents."""

from .core import mcp
from .middleware import MCPAuthMiddleware
from . import tools  # noqa: F401 — registers all tools via side-effect


def get_mcp_app():
    """Return the MCP Starlette app with auth middleware."""
    mcp_app = mcp.http_app(path="/mcp")
    mcp_app.add_middleware(MCPAuthMiddleware)
    return mcp_app
