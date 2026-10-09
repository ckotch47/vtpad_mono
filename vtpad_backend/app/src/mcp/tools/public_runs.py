from fastmcp.server.dependencies import get_http_request
import logging

from ..core import mcp
from ...public_run.service import (
    create_public_link as create_link,
    get_shared_run as redeem_shared_run,
    revoke_public_link as revoke_link,
)


class _PublicRunTokenLogFilter(logging.Filter):
    """Redact the share token from FastMCP's debug argument log and errors."""

    def filter(self, record):
        if record.name.endswith('mixins.mcp_operations'):
            arguments = record.args
            if (
                isinstance(arguments, tuple)
                and len(arguments) >= 2
                and arguments[0] == 'get_shared_run'
                and isinstance(arguments[1], dict)
            ):
                redacted = dict(arguments[1])
                if 'share_token' in redacted:
                    redacted['share_token'] = '[REDACTED]'
                record.args = (arguments[0], redacted, *arguments[2:])
        elif record.name.endswith('server.server'):
            # Validation errors may serialize rejected input values.
            args = record.args if isinstance(record.args, tuple) else ()
            if 'get_shared_run' in str(record.msg) or (args and args[0] == 'get_shared_run'):
                record.msg = 'FastMCP public run tool event (details redacted)'
                record.args = ()
        return True


logging.getLogger('fastmcp.server.mixins.mcp_operations').addFilter(_PublicRunTokenLogFilter())
logging.getLogger('fastmcp.server.server').addFilter(_PublicRunTokenLogFilter())


@mcp.tool()
async def create_public_run_link(run_id: str) -> dict:
    """Create a seven-day public link; the bearer token is returned once."""
    return await create_link(run_id, get_http_request())


@mcp.tool()
async def revoke_public_run_link(run_id: str) -> dict:
    """Revoke the active public link for a run."""
    return await revoke_link(run_id, get_http_request())


@mcp.tool()
async def get_shared_run(share_token: str) -> dict:
    """Redeem a public run token using the same safe projection as REST."""
    return await redeem_shared_run(share_token, get_http_request())
