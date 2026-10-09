import json

MAX_CASE_TEMPLATE_REQUEST_BYTES = 1024 * 1024
CASE_TEMPLATE_PATH_PREFIX = '/api/v2/test-case-template/'


class CaseTemplateBodyLimitMiddleware:
    """Bound template mutation bodies before FastAPI parses or stores them."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or not scope.get('path', '').startswith(CASE_TEMPLATE_PATH_PREFIX) or scope.get('method') not in {'POST', 'PUT', 'PATCH'}:
            return await self.app(scope, receive, send)

        headers = {key.lower(): value for key, value in scope.get('headers', [])}
        content_length = headers.get(b'content-length')
        if content_length is not None:
            try:
                if int(content_length) > MAX_CASE_TEMPLATE_REQUEST_BYTES:
                    return await self._too_large(scope, send)
            except ValueError:
                return await self._too_large(scope, send)

        body = bytearray()
        more_body = True
        while more_body:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            chunk = message.get('body', b'')
            if len(body) + len(chunk) > MAX_CASE_TEMPLATE_REQUEST_BYTES:
                return await self._too_large(scope, send)
            body.extend(chunk)
            more_body = message.get('more_body', False)

        sent = False

        async def replay_receive():
            nonlocal sent
            if sent:
                return {'type': 'http.request', 'body': b'', 'more_body': False}
            sent = True
            return {'type': 'http.request', 'body': bytes(body), 'more_body': False}

        await self.app(scope, replay_receive, send)

    @staticmethod
    async def _too_large(scope, send):
        payload = json.dumps({'detail': 'Request body exceeds the 1 MiB limit'}).encode()
        await send({
            'type': 'http.response.start', 'status': 413,
            'headers': [(b'content-type', b'application/json'), (b'content-length', str(len(payload)).encode())],
        })
        await send({'type': 'http.response.body', 'body': payload})
