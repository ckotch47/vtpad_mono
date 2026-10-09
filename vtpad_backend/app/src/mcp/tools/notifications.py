"""MCP read tools for the current user's in-app notifications."""

from ..core import mcp
from ..utils import _get_user_id
from ...notification.dto import GetNotificationDto
from ...notification.service import NotificationService


@mcp.tool()
async def get_notifications(skip: int = 0, limit: int = 20) -> list[dict]:
    """List notifications visible to the authenticated user."""
    rows = await NotificationService.get_notification(
        GetNotificationDto(user_id=_get_user_id()), limit=limit, skip=skip
    )
    return [
        {
            "id": str(row["id"]),
            "create_date": row["create_date"].isoformat(),
            "event": row["event"],
            "data": row["data"],
            "read": row["read"],
        }
        for row in rows
    ]


@mcp.tool()
async def get_unread_notification_count() -> int:
    """Count notifications visible to the authenticated user that remain unread."""
    return await NotificationService.get_count_unread_notification(_get_user_id())


@mcp.tool()
async def mark_notification_read(notification_id: str) -> dict | bool:
    """Mark one of the authenticated user's currently visible notifications read."""
    return await NotificationService.read_notification(notification_id, _get_user_id())


@mcp.tool()
async def mark_all_notifications_read() -> int:
    """Mark all currently visible notifications read for the authenticated user."""
    return await NotificationService.read_all_notification(_get_user_id())
