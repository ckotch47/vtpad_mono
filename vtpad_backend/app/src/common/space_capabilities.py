"""Resolve effective write capabilities for a principal in one space."""

import json
from typing import Any

from fastapi import HTTPException
from starlette.requests import Request
from tortoise import Tortoise

from .crypto import user_payload


SPACE_WRITE_CAPABILITIES = (
    "cases",
    "suites",
    "sections",
    "plans",
    "runs",
    "results",
    "bugs",
    "bug_comments",
    "tags",
    "tech_docs",
    "traceability",
    "run_bug_links",
)


def _decode_rights(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            return {}
        return decoded if isinstance(decoded, dict) else {}
    return {}


def _capabilities_from_rights(rights: dict[str, Any]) -> dict[str, bool]:
    can_write_cases = rights.get("editItems") is True
    can_write_suites = rights.get("editPads") is True
    can_write_runs = rights.get("editRuns") is True
    can_write_bugs = rights.get("manageBugs", True) is True
    can_write_tech_docs = rights.get("editTechDocs", True) is True
    can_write = not (rights.get("readOnly") is True)

    return {
        "cases": can_write and can_write_cases,
        "suites": can_write and can_write_suites,
        "sections": can_write and can_write_cases,
        "plans": can_write and can_write_suites,
        "runs": can_write and can_write_runs,
        "results": can_write and can_write_runs,
        "bugs": can_write and can_write_bugs,
        "bug_comments": can_write and can_write_bugs,
        "tags": can_write and rights.get("editTags") is True,
        "tech_docs": can_write and can_write_tech_docs,
        "traceability": can_write and can_write_cases and can_write_tech_docs,
        "run_bug_links": can_write and can_write_runs and can_write_bugs,
    }


async def get_space_capabilities(user_id: str, space_id: str) -> dict[str, bool]:
    """Return effective domain write capabilities or reject an inaccessible space."""
    conn = Tortoise.get_connection("default")
    rows = await conn.execute_query_dict(
        """
        SELECT su.role AS space_role,
               su."right" AS space_right,
               u.role AS company_role
        FROM spacemodel s
        LEFT JOIN spacesusermodel su
            ON su."spaceId" = s.id
            AND su."userId" = $1
        LEFT JOIN usercompanysettingsmodel u
            ON u.user_id = $1
            AND u.company_id = s.company_id
            AND u.status = 'active'
        WHERE s.id = $2
        """,
        [user_id, space_id],
    )
    if not rows:
        raise HTTPException(status_code=403, detail="not right space")

    principal = rows[0]
    company_role = principal.get("company_role")
    space_role = principal.get("space_role")
    is_active_member = bool(space_role) and bool(company_role)
    is_active_company_admin = company_role == "company_admin"
    if not (is_active_member or is_active_company_admin):
        raise HTTPException(status_code=403, detail="not right space")

    if space_role == "OWNER" or is_active_company_admin:
        return {name: True for name in SPACE_WRITE_CAPABILITIES}

    rights = _decode_rights(principal.get("space_right"))
    return _capabilities_from_rights(rights)


async def require_space_capability(
    user_id: str,
    space_id: str,
    capability: str,
) -> None:
    if capability not in SPACE_WRITE_CAPABILITIES:
        raise ValueError(f"Unknown space capability: {capability}")

    capabilities = await get_space_capabilities(user_id, space_id)
    if not capabilities[capability]:
        raise HTTPException(status_code=403, detail="not have right")


async def require_request_space_capability(
    space_id: str,
    request: Request,
    capability: str,
) -> None:
    """Resolve the actor from the authenticated REST or MCP request and enforce a write right."""
    user_id = getattr(request.state, "mcp_authenticated_user_id", None)
    if user_id is None:
        authorization = request.headers.get("authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="not authenticated")
        user_id = user_payload(token).get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="not authenticated")
    await require_space_capability(str(user_id), str(space_id), capability)
