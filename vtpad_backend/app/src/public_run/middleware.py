class PublicRunLinkHeadersMiddleware:
    """Apply leakage-prevention headers on public-link and management responses."""

    _paths = {
        '/api/v2/test-run/public/shared',
        # MCP creation returns its one-time token in the JSON-RPC result.
        '/api/v1/mcp',
    }

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        path = scope.get('path', '')
        protected = path in self._paths or (
            path.startswith('/api/v2/test-run/') and path.endswith('/public-link')
        )
        if not protected:
            await self.app(scope, receive, send)
            return

        async def add_headers(message):
            if message['type'] == 'http.response.start':
                headers = list(message.get('headers', []))
                headers.extend([
                    (b'cache-control', b'no-store'),
                    (b'referrer-policy', b'no-referrer'),
                    (b'x-robots-tag', b'noindex'),
                ])
                message['headers'] = headers
            await send(message)

        await self.app(scope, receive, add_headers)
