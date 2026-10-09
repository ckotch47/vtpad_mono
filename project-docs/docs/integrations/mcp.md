# MCP integration

## Endpoint and authentication

The FastMCP HTTP application is mounted by the backend at `/v1/mcp` (JSON-RPC over HTTP/SSE). MCP requests use `Authorization: Bearer <API token>`. `MCPAuthMiddleware` validates the token and records the authenticated user in request state; shared space guards use that identity for authorization.

## Section ordering

The `sort_sections` tool reorders one section within its current sibling group. Supply `section_id` and exactly one of `sort_before_id` or `sort_after_id`. The target and neighbor must share both suite and parent. The tool calls the same `SectionService.update_sort` implementation as REST, which derives the space from the target's suite, checks the user's membership, and updates sibling positions transactionally.

The result is a JSON array of siblings ordered by `sort`, with `id`, `name`, `description`, `suite_id`, `parent_id`, and `sort`. A membership failure is surfaced as an MCP tool error. Invalid neighbor combinations and non-sibling references are rejected by the shared DTO/service validation.

## Registration

MCP tools are registered through imports in `app/src/mcp/tools/__init__.py`; section tools live in `app/src/mcp/tools/sections.py`. The HTTP application and authentication middleware are defined in `app/src/mcp/server.py` and `app/src/mcp/middleware.py`.

## Traceability matrix

`get_traceability_matrix(space_id, tech_doc_ids?)` calls the same read service as `GET /api/v2/traceability/space/{space_id}/matrix`. Omit `tech_doc_ids` to include all Tech Docs in the space; pass IDs to select requirements. The result contains linked cases, each case's latest result and run, per-requirement coverage, and explicit counts for requirements without cases and cases without results. Legacy cross-space links are excluded. Tech Doc rich text is returned in escaped `content_display` form, safe to render as text but without HTML formatting.

## Case templates

`list_test_case_templates`, `get_test_case_template`, `list_test_case_template_versions`, `get_test_case_template_version`, `create_test_case_template`, `update_test_case_template`, and `use_test_case_template` mirror the REST template endpoints and share their space-scoped service. List/read responses bound history to metadata and pages; selected-version reads return one content snapshot. Each content update creates an immutable numbered version when fields change. `use_test_case_template` requires the resulting case title and supports optional suite/section, version number, allowlisted field overrides, and up to 50 typed custom-field values (64 KiB serialized maximum), validated against definitions in the same space through the existing testcase creation path. REST mutations and MCP template mutation calls are limited to 1 MiB; other MCP tools retain their 8 MiB transport cap. Template content strings are limited to 32,768 characters, description to 4,096, serialized content to 128 KiB, estimated duration to 0–2,147,483,647 seconds, and each template to 100 versions. Custom fields are excluded from template content/version history. Templates and cases have no live reference, so updating a template never changes previously created cases.
### Data exchange

- `export_space_data(space_id, format="json"|"csv", suite_ids?)`
- `preview_space_import(space_id, content, format="json"|"csv")`
- `import_space_data(space_id, content, idempotency_key, format="json"|"csv")`

These tools call the same service and return the same versioned content/preview/result shapes as REST. Imports are bounded, space-scoped, atomic, reject read-only collaborators, and replay the original outcome for a matching actor, space, idempotency key, and content. Import does not send case content to embedding providers. CSV export neutralizes formula-like text cells; portable files do not contain snapshots, run history, users, attachments, or secrets.

`update_test_result` treats omitted `comment` and `duration_seconds` as unchanged, matching REST PATCH semantics. Set `clear_comment` or `clear_duration` to `true` to explicitly clear either value.

### CI/CD webhooks

- `create_webhook_integration(payload)`
- `get_webhook_integration(integration_id)`
- `rotate_webhook_integration_credential(integration_id)`
- `revoke_webhook_integration(integration_id)`
- `process_webhook_event(payload)`

Management tools use the same owner/company-admin plus active membership checks as REST. The secret is returned only during create or rotate. `process_webhook_event` supplies `integration_id`, signed `method`, exact `path`, `timestamp`, `nonce`, `idempotency_key`, hex `signature`, and JSON `body`; it invokes the same bounded, allowlist-scoped service as the HTTP callback. The MCP HTTP transport rejects request bodies larger than 8 MiB before FastMCP parses tool arguments, and the webhook `body` field is limited to 1 MiB before UTF-8 encoding. Timestamp and nonce bounds match REST: 1–12 ASCII digits and 16–128 printable ASCII characters. The canonical path is `/api/v2/webhooks/integrations/{integration_id}/callback`. Result detail adds only safe source metadata; secrets and payloads are not part of the result representation. Verified signed attempts, including rejected payloads, count toward the 60/minute integration limit. Invalid-auth attempts have a separate 120/minute cap; after the cap they receive 429 without consuming the verified quota. Redacted audit records are retained for 30 days, failure buckets for 24 hours, and nonce rows for 10 minutes; cleanup is opportunistic and uses no scheduled job.
