"""MCP auth middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from ..api_token.service import ApiTokenService
import logging

logger = logging.getLogger(__name__)


class MCPAuthMiddleware(BaseHTTPMiddleware):
    """Verify API Bearer token and attach user_id to request state."""

    async def dispatch(self, request: Request, call_next):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse({"error": "Missing or invalid Authorization header"}, status_code=401)

        raw_token = auth.replace("Bearer ", "")
        try:
            api_token = await ApiTokenService.validate_token(raw_token)
            request.state.user_id = str(api_token.user_id)
            request.state.api_token_id = str(api_token.id)
            request.state.api_token_scopes = api_token.scopes or []
        except Exception as e:
            logger.error('Unexpected error: %s', e, exc_info=True)
            return JSONResponse({"error": "Invalid or expired API token"}, status_code=401)

        return await call_next(request)
