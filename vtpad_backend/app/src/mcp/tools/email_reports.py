from datetime import date
from uuid import UUID

from fastmcp.server.dependencies import get_http_request

from ..core import mcp
from ...email_report.dto import EmailReportPreviewDto, EmailReportRecipientConfirmation, EmailReportSendDto
from ...email_report.service import EmailReportService


@mcp.tool()
async def get_qa_report_email_recipients(space_id: str) -> list[dict]:
    """List active, explicitly assigned members of a space who can receive QA reports."""
    return await EmailReportService.get_recipients(UUID(space_id), get_http_request())


@mcp.tool()
async def preview_qa_email_report(
    space_id: str,
    date_start: str,
    date_end: str,
    fields: list[str],
    create_user: str | None = None,
) -> dict:
    """Create an immutable, bounded QA report snapshot for later manual email delivery."""
    dto = EmailReportPreviewDto(
        space_id=UUID(space_id),
        date_start=date.fromisoformat(date_start),
        date_end=date.fromisoformat(date_end),
        fields=fields,
        create_user=UUID(create_user) if create_user else None,
    )
    return await EmailReportService.create_preview(dto, get_http_request())


@mcp.tool()
async def send_qa_email_report(
    snapshot_id: str,
    recipient_ids: list[str],
    confirmed_recipients: list[dict[str, str]],
    idempotency_key: str,
) -> dict:
    """Manually send one individual email per active member using a previewed snapshot."""
    dto = EmailReportSendDto(
        snapshot_id=UUID(snapshot_id),
        recipient_ids=[UUID(value) for value in recipient_ids],
        confirmed_recipients=[
            EmailReportRecipientConfirmation(
                recipient_id=UUID(recipient['recipient_id']),
                email=recipient['email'],
            )
            for recipient in confirmed_recipients
        ],
        idempotency_key=UUID(idempotency_key),
    )
    return await EmailReportService.send(dto, get_http_request())
