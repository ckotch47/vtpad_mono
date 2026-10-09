"""MCP Server for VTPad — exposes test management tools to local AI agents."""

import json

from .core import mcp
from .middleware import MCPAuthMiddleware
from . import tools  # noqa: F401 — registers all tools via side-effect

MCP_MAX_REQUEST_BYTES = 8 * 1024 * 1024


class MCPRequestBodyLimitMiddleware:
    """Bound raw MCP JSON before FastMCP parses tool arguments."""

    def __init__(self, app, max_bytes: int = MCP_MAX_REQUEST_BYTES):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope.get('method') not in ('POST', 'PUT', 'PATCH'):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get('headers', []))
        content_length = headers.get(b'content-length')
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    await self._reject(send)
                    return
            except ValueError:
                await self._reject(send)
                return

        chunks = []
        size = 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            chunk = message.get('body', b'')
            size += len(chunk)
            if size > self.max_bytes:
                await self._reject(send)
                return
            chunks.append(chunk)
            if not message.get('more_body', False):
                break

        body = b''.join(chunks)
        sent = False

        async def replay_receive():
            nonlocal sent
            if sent:
                return {'type': 'http.request', 'body': b'', 'more_body': False}
            sent = True
            return {'type': 'http.request', 'body': body, 'more_body': False}

        await self.app(scope, replay_receive, send)

    @staticmethod
    async def _reject(send):
        body = json.dumps({'detail': 'MCP request exceeds the 8 MiB transport limit'}).encode()
        await send({'type': 'http.response.start', 'status': 413, 'headers': [
            (b'content-type', b'application/json'),
            (b'content-length', str(len(body)).encode()),
        ]})
        await send({'type': 'http.response.body', 'body': body})


def get_mcp_app():
    """Return the MCP Starlette app with auth middleware."""
    mcp_app = mcp.http_app(path="/mcp")
    mcp_app.add_middleware(MCPRequestBodyLimitMiddleware)
    mcp_app.add_middleware(MCPAuthMiddleware)
    return mcp_app
