# Backend Modules Endpoint Index

## Operational checks

- `GET /health` — public liveness probe.
- `GET /ready` — public readiness probe for PostgreSQL and Redis; returns a generic `503` if either dependency is unavailable or times out.

## Что описывает

Индекс модулей backend'а с перечнем endpoint'ов по каждому модулю.

## Preconditions

- Все роутеры зарегистрированы в `app/main.py`.
- Пути указаны с префиксом `/api` (основной вариант через `register_router`).

## Модули

### `app/src/auth`
- `POST /api/v1/auth`
- `POST /api/v1/auth/refresh`

### `app/src/users`
- `POST /api/v1/user`
- `GET /api/v1/user`
- `PATCH /api/v1/user`
- `GET /api/v1/user/search/by-mail`

### `app/src/space`
- `GET /api/v1/space`
- `POST /api/v1/space`
- `GET /api/v1/space/{space_id}`
- `GET /api/v1/space/{space_id}/users`
- `PUT /api/v1/space/{space_id}`
- `PUT /api/v1/space/{space_id}/user`
- `DELETE /api/v1/space/{space_id}/user/{user_id}`
- `PATCH /api/v1/space/{space_id}/user/{user_id}` — owner/active same-company admin may explicitly set `readOnly`, `manageBugs`, and `editTechDocs`; false values are persisted.
- `PUT /api/v1/space/{space_id}/user-make-owner/{user_id}`
- `DELETE /api/v1/space/{space_id}`
- `GET /api/v1/space/{space_id}/all_runs`
- `GET /api/v1/space/{space_id}/statistic`
- `GET /api/v1/space/by-short/{short_name}`

### `app/src/pad`
- `GET /api/v1/pad/{space_id}`
- `GET /api/v1/pad/detail/{pad_id}`
- `POST /api/v1/pad/{space_id}`
- `PATCH /api/v1/pad/{pad_id}`
- `DELETE /api/v1/pad/{pad_id}`
- `PATCH /api/v1/pad/sort/{pad_id}`

### `app/src/padfolder`
- `GET /api/v1/pad-folder/{space_id}`
- `GET /api/v1/pad-folder/detail/{folder_id}`
- `POST /api/v1/pad-folder/{space_id}`
- `PATCH /api/v1/pad-folder/{folder_id}`
- `DELETE /api/v1/pad-folder/{folder_id}`

### `app/src/run`
- `POST /api/v1/runs/{pad_id}`
- `DELETE /api/v1/runs/{run_id}`
- `GET /api/v1/runs/items/{run_id}`
- `GET /api/v1/runs/{run_id}`
- `GET /api/v1/runs/all/{pad_id}`
- `GET /api/v1/runs/filter/{space_id}`
- `GET /api/v1/runs/by-filter/{space_id}`
- `PATCH /api/v1/runs/{run_id}`

### `app/src/runitems`
- `PATCH /api/v1/runitems/{item_id}`

### `app/src/items`
- `GET /api/v1/items/{pad_id}`
- `POST /api/v1/items/{pad_id}`
- `PUT /api/v1/items/{item_id}`
- `DELETE /api/v1/items/{item_id}`
- `PATCH /api/v1/items/{item_id}`

### `app/src/bug`
Bug create/update require `bugs`; bug tag assignments require both `bugs` and `tags`. State transitions to closed/hold and reopen require `closeBugs` in addition to `bugs`, with owner and active same-company admin bypass.
- `POST /api/v1/bugs`
- `GET /api/v1/bugs`
- `GET /api/v1/bugs/detail/{bug_id}`
- `GET /api/v1/bugs/detail-short`
- `GET /api/v1/bugs/id/by-short`
- `PUT /api/v1/bugs/{bug_id}`
- `GET /api/v1/bugs/filters`
- `PUT /api/v1/bugs/{bug_id}/tag`
- `DELETE /api/v1/bugs/{bug_id}/tag/{tag_id}`
- `GET /api/v1/bugs/state-enum`
- `GET /api/v2/bugs/space/{space_id}/by-link/{link_uuid}`

### `app/src/analytics`
- `GET /api/v2/analytics/space/{space_id}/quality`
- `GET /api/v2/analytics/space/{space_id}/quality/results`
- `GET /api/v2/analytics/space/{space_id}/time`
- `GET /api/v2/analytics/space/{space_id}/bugs`
- `GET /api/v2/analytics/space/{space_id}/bugs/by-run`
- `GET /api/v2/analytics/space/{space_id}/bugs/by-suite`

Linked-defect analytics use explicit UUID links only and require space membership. Bug/run joins enforce the same space. Each bug list item contains at most 25 `result_links`; `link_count` remains the full count and `result_links_truncated` indicates omitted navigation pairs.

Quality and time endpoints require current space membership and share their service with MCP tools `get_quality_trends`, `get_quality_results` and `get_time_trends`. The paginated quality-results route/tool returns run/result source IDs for one UTC week and suite. Historical suite attribution uses `testcase_snapshot.suite_id`; unresolved legacy attribution is grouped as `Unknown / mixed suite`. The single run timer is attributed once by `test_run.suite_id`, never once per case suite.

### `app/src/comments`
Comment create/update/delete require `bug_comments` on the parent bug space; update/delete keep the existing author-only rule.
- `GET /api/v1/comment/{bug_id}`
- `POST /api/v1/comment/{bug_id}`
- `PUT /api/v1/comment/{comment_id}`
- `DELETE /api/v1/comment/{comment_id}`

### `app/src/tag`
Tag create/update/delete require the server-derived `tags` capability.
- `GET /api/v1/tag/{space_id}`
- `PUT /api/v1/tag/{tag_id}`
- `POST /api/v1/tag/{space_id}`
- `DELETE /api/v1/tag/{tag_id}`

### `app/src/testcases`
- `GET /api/v1/testcases/filter/{space_id}`
- `GET /api/v1/testcases/{space_id}`
- `GET /api/v1/testcases/paditem/{paditem_id}`
- `GET /api/v1/testcases/detail/{testcase_id}`
- `GET /api/v1/testcases/item/{item_id}`
- `POST /api/v1/testcases`
- `PATCH /api/v1/testcases/{testcase_id}`
- `POST /api/v1/testcases/image/{testcase_id}`
- `DELETE /api/v1/testcases/image/{testcase_id}/{image_id}`
- `DELETE /api/v1/testcases/{testcase_id}`
- `GET /api/v1/testcases/shortname/{short_name}`

### `app/src/testcases_paditem`
- `PUT /api/v1/testcases-paditem/{item_id}/{testcase_id}`
- `DELETE /api/v1/testcases-paditem/{item_id}/{testcase_id}`

### `app/src/testcases_runitem`
- `PATCH /api/v1/testcases-runitem/{element_id}`

### `app/src/section`
- `GET /api/v2/section/suite/{suite_id}`
- `GET /api/v2/section/suite/{suite_id}/tree`
- `GET /api/v2/section/{section_id}` — all section reads require access to the owning suite's space; MCP `get_section` applies the same check.
- `POST /api/v2/section/`
- `PATCH /api/v2/section/{section_id}`
- `DELETE /api/v2/section/{section_id}`
- `PATCH /api/v2/section/sort/{section_id}` — JSON body contains exactly one of `sort_before_id` or `sort_after_id`; neighbor must have the same suite and parent; requires the `sections` write capability; returns ordered siblings.

### `app/src/test_suite`
- `GET /api/v2/test-suite/space/{space_id}`
- `GET /api/v2/test-suite/{suite_id}` — requires access to the suite's space.
- `POST /api/v2/test-suite/`
- `PATCH /api/v2/test-suite/{suite_id}`
- `DELETE /api/v2/test-suite/{suite_id}`
- `PATCH /api/v2/test-suite/sort/{suite_id}`

All suite writes require the server-derived `suites` capability. REST and MCP suite update/delete/hard-delete operations resolve the suite's space before mutation; reorder references must remain in that same space.

### `app/src/checklist`
- `GET /api/v1/checklist/list/{space_id}`
- `GET /api/v1/checklist/{checklist_id}`
- `POST /api/v1/checklist/{space_id}`
- `PATCH /api/v1/checklist/{checklist_id}`
- `DELETE /api/v1/checklist/{checklist_id}`
- `GET /api/v1/checklist/by-short/{short_name}`

### `app/src/file`
- `POST /api/v1/file`
- `POST /api/v1/file/image`
- `GET /api/v1/file/{file_id}`

### `app/src/notification`
- `GET /api/v1/notification/stream`
- `GET /api/v1/notification/unread-count`
- `GET /api/v1/notification`
- `PUT /api/v1/notification/{notification_id}/read`
- `PUT /api/v1/notification/read-all`
- MCP `get_notifications`, `get_unread_notification_count`, `mark_notification_read` and `mark_all_notifications_read`

`RUN_COMPLETED` создаётся в транзакции успешного завершения run, адресуется только `created_by`, защищён уникальным индексом `(run_id, event, user_id)` и содержит только opaque `run_id` и route. Список, unread count, SSE и mark-read исключают run события после отзыва доступа к space.

MCP работает как Streamable HTTP по `/api/v1/mcp`: сервер передаёт JSON-RPC ответы SSE-событиями; клиенты должны читать поток до ответа с нужным `id`. Ограничитель тела запроса после replay исходного body передаёт дальнейшие ASGI receive events транспорту, чтобы не блокировать SSE/disconnect handling.

### `app/src/news`
- `GET /api/v1/news`
- `PATCH /api/v1/news/read`
- `GET /api/v1/news/unread`

### `app/src/report`
- `GET /api/v1/report/test/list/{space_id}`
- `GET /api/v1/report/test/detail/{test_id}`

### `app/src/qa_report`
- `GET /api/qa-report/users`
- `GET /api/qa-report/bug-list`

### `app/src/email_report`
- `GET /api/qa-report/email/recipients/{space_id}` — возвращает только активных пользователей с явным членством в указанном space.
- `POST /api/qa-report/email/preview` — серверная выборка до 500 строк на секцию, allowlist полей, payload до 256 KiB, неизменяемый snapshot со сроком 24 часа.
- `POST /api/qa-report/email/send` — до 10 получателей, только адреса из актуального членства; клиент передаёт подтверждённые адреса как compare-only constraint, а адрес доставки повторно берётся из БД. Отдельное HTML-письмо каждому, durable idempotency receipts; REST и MCP используют один сервис. После неопределённого сетевого результата UI сохраняет ключ запроса.

### `app/src/notes`
- `GET /api/v1/notes/{space_id}`
- `POST /api/v1/notes/{space_id}`
- `PATCH /api/v1/notes/{note_id}`
- `DELETE /api/v1/notes/{note_id}`

### `app/src/admin/company`
- `GET /api/v2/amin/company/list`
- `POST /api/v2/amin/company`
- `PUT /api/v2/amin/company/{company_id}`
- `GET /api/v2/amin/company/detail/{company_id}`
- `GET /api/v1/company/detail/{company_id}`

### `app/src/admin/user_company_settings`
- `GET /api/v2/company-user/list`
- `PUT /api/v2/company-user/{user_id}`
- `POST /api/v2/company-user`
- `PUT /api/v2/company-user/{user_id}/reset-password`
- `DELETE /api/v2/company-user/{user_id}`

### `app/src/mcp`
- `POST /v1/mcp` (MCP JSON-RPC over HTTP/SSE)

MCP tools in `app/src/mcp/tools/*` are not classic REST endpoints, but they are part of public integration surface.

Current behavior constraints (synced with code):
- Space capabilities are available in `GET /api/v1/space/{space_id}` and through MCP `get_space_capabilities(space_id)`; both expose the same server-derived per-domain write booleans.
- `get_space_suites` transforms items returned by `TestSuiteService.get_by_space(...)` as dictionaries.
- MCP `search_test_cases` accepts the same type/status/suite/priority/tag filters and one-based `page`/`limit` pagination as the REST case list; `suite_id="none"` searches unassigned cases. It returns the requested page as a list, preserving the MCP result shape. `get_space_suites` accepts optional `search`, `status`, and one-based `page`/`limit`, and checks access to `space_id` before querying; it also preserves its list result shape.
- MCP plan tools provide equivalent read/write access plus `preview_test_plan_selection`; create/update accept `suite_ids` and typed `filters`, and list `case_count` is computed by the shared resolver.
- `duplicate_test_case` uses Bearer token from `Authorization` header when calling `TestCaseService.duplicate(...)`.
- `MCPAuthMiddleware` enforces `text/event-stream; charset=utf-8` on MCP SSE responses.
- Space access checks invoked by MCP tools use `request.state.mcp_authenticated_user_id`, which is populated only by `MCPAuthMiddleware` after API-token validation; REST requests continue to resolve the user from their JWT Bearer token.
- Test-run MCP lifecycle includes `start_test_run`, `pause_test_run`, `resume_test_run` and `complete_test_run`; `get_run_results` returns the same timer and duration aggregates as REST. `compare_test_runs` returns the same snapshot-only comparison projection and same-space/completed-run checks as REST. Testcase MCP create/update/read and result updates expose the estimate and validated actual duration.
- `sort_sections` reorders one section relative to exactly one before/after sibling; it uses the same `SectionSortDto` and `SectionService.update_sort` as REST, and returns JSON siblings with `id`, `name`, `description`, `suite_id`, `parent_id`, `sort`.
- Custom-field tools `list_custom_fields`, `create_custom_field`, `update_custom_field`, `delete_custom_field`, `get_custom_field_values`, and `set_custom_field_value` call the same space-authorized services as REST. MCP testcase create/update accepts `custom_fields: [{field_id, value}]`; testcase detail/search/list reads and run result snapshots return self-contained field metadata and values. Collection responses batch-load fields for the selected cases.
- Custom field values are validated against their definition type/options and entity type; foreign-space field/entity pairs are hidden as `404`. Required definitions default to false; requiredness is supported for testcase fields.

### `app/src/test_plan`
- `GET /api/v2/test-plan/space/{space_id}`
- `POST /api/v2/test-plan/preview-selection`
- `GET /api/v2/test-plan/{plan_id}`
- `GET /api/v2/test-plan/{plan_id}/cases`
- `POST /api/v2/test-plan/`
- `PATCH /api/v2/test-plan/{plan_id}`
- `DELETE /api/v2/test-plan/{plan_id}`

Every REST and MCP operation checks access to the plan's space. Plan sources are the union of selected suites and explicit testcase IDs; with no sources the candidate set is empty. Priority, all-tags, and typed custom-field filters intersect that candidate set. Preview, list count, and run creation use the same resolver. Existing plans default to no filters. PATCH omission preserves filters and an empty object clears them. Run creation evaluates saved plan filters with the source and testcase snapshots in one PostgreSQL `REPEATABLE READ` transaction.

### `app/src/test_run`
- `POST /api/v2/test-run/preview`
- `POST /api/v2/test-run`
- `GET /api/v2/test-run/space/{space_id}`
- The run list accepts an optional status filter and returns `completed_at` so completed runs can be searched and paginated in the comparison selector.
- `GET /api/v2/test-run/{run_id}/compare/{other_run_id}` compares two completed runs in one space by immutable testcase snapshots. It reports added/removed testcase IDs, changed snapshot fields, result status/comment/duration deltas, and explicitly unknown fields for incomplete legacy snapshots; it never falls back to the current testcase. MCP exposes the same projection through `compare_test_runs`.
- `GET/PATCH/DELETE /api/v2/test-run/{run_id}`
- `POST /api/v2/test-run/{run_id}/start`
- `POST /api/v2/test-run/{run_id}/pause`
- `POST /api/v2/test-run/{run_id}/resume`
- `POST /api/v2/test-run/{run_id}/complete`
- `PATCH /api/v2/test-run/result/{result_id}`
- `POST /api/v2/test-run/result/{result_id}/bugs/{bug_uuid}`
- `DELETE /api/v2/test-run/result/{result_id}/bugs/{bug_uuid}`
- `POST/DELETE /api/v2/test-run/result/{result_id}/bugs/link` (legacy short-name wrappers)
- `POST /api/v2/test-run/result/{result_id}/bugs` (quick create and link)
- `PATCH /api/v2/test-run/result/bulk`
- Test plan create/update/delete require `plans`; run create/update/lifecycle/delete and public-link rotation/revocation require `runs`. Result edits require `results`, and result bug-link mutations require combined `run_bug_links`. REST and MCP use the same server-side checks.

Run detail results include nullable `source`. Webhook-sourced results contain only `type`, integration ID/name, request ID, and update time. Manual result edits clear provenance transactionally.

### `app/src/webhook_integration`
- `POST /api/v2/webhooks/integrations`
- `GET /api/v2/webhooks/integrations/{integration_id}`
- `POST /api/v2/webhooks/integrations/{integration_id}/rotate`
- `POST /api/v2/webhooks/integrations/{integration_id}/revoke`
- `POST /api/v2/webhooks/integrations/{integration_id}/callback` (signed callback; no JWT)

MCP exposes `create_webhook_integration`, `get_webhook_integration`, `rotate_webhook_integration_credential`, `revoke_webhook_integration`, and `process_webhook_event`; each uses the corresponding shared service. Secrets are returned only once on create/rotate. Callback requests update only pre-mapped results in explicitly allowlisted active runs.

Run creation snapshots the selected test cases in the same transaction as the new results. A suite, plan, or explicit case selection can include test cases of any status; source validation is limited to source and space membership. Results can be corrected while their run is active; returning a result to `not_run` clears execution attribution and timestamp. List responses for test runs, test cases, test suites and test plans, as well as testcase detail, include a nullable creator `{id, username}` without email.
Run detail keeps the compatible `linked_bug_ids` field as an array and exposes the original legacy JSON as `linked_bug_ids_raw`, including `NULL`, duplicates, and ambiguous historical short names. New `linked_bugs` rows use `bugsmodel.link_uuid` and return `{id, short_name, title}`; REST and MCP use the same service. Legacy short-name link tools only work when exactly one bug in the run space has that name. Quick create takes a client-generated `operation_id`; matching retries return the original bug, mismatched reuse returns `409`, and retry after deletion of the original bug returns `410`. New bug short names are allocated while holding the space row lock; no uniqueness constraint is imposed on historical short names. Run detail also includes a shared timer summary (`state`, calendar/active/paused seconds and interval count), plus the sum of known case durations and measured/unmeasured result counts. Legacy runs without timer intervals report active and paused duration as unknown. The API calculates timer values from stored interval boundaries on request; there is no cron/background timer loop, and the UI refreshes on load, state changes, or explicit refresh. Estimated testcase duration is versioned and copied into each result snapshot; existing records remain `NULL`. New run snapshots and preview items include `suite_id`, `suite_name`, and the root-to-leaf `section_path` (`id`, `name`, `sort` per section). Existing `section` fields remain; old snapshots without a full path are served with only their known section.

### `app/src/public_run`

Public run links have a dedicated table and safe projection. REST and MCP create/revoke/redeem use the same service; management requires an active same-space member who is the run creator or space owner, with same-company admins also required to have active space membership. The 256-bit bearer token is returned only at creation, stored as a versioned HMAC digest, expires after seven days, and is rotated/revoked atomically. Redemption returns only run name/status and group names, case/status counts, and known duration totals. Redis applies shared limits of 30 requests/minute/token and 120/minute/client IP; failures fail closed. The server flag `PUBLIC_RUN_LINKS_ENABLED` defaults off until security acceptance. REST uses `Authorization: Bearer`; frontend share tokens are delivered in the URL fragment, removed before redemption, and never sent in query/path/referrer.

MCP keeps `link_bug_to_result` and `unlink_bug_from_result` data semantics: they add/remove a short name in legacy `linked_bug_ids`. They now require an active run and exactly one matching bug in the run space; a missing match returns `404`, while an ambiguous name or inactive run returns `409`. Consumers that used these tools on draft/completed runs must switch to active runs. New UUID links use `link_bug_uuid_to_result` and `unlink_bug_uuid_from_result`. UUID tools and REST endpoints treat their UUID as `link_uuid`; quick-create returns that value as `bug_uuid`, while nested `bug.id` remains the legacy ID. `create_and_link_bug_to_result` uses the same idempotent operation contract as REST. `update_test_result` validates legacy short-name values against the run space and does not modify UUID links.

### `app/src/tech_doc`
- `GET /api/v2/tech-doc/space/{space_id}`
- `GET /api/v2/tech-doc/space/{space_id}/tree`
- `GET /api/v2/tech-doc/{doc_id}`
- `POST /api/v2/tech-doc/`
- `PATCH /api/v2/tech-doc/{doc_id}`
- `DELETE /api/v2/tech-doc/{doc_id}`

### `app/src/data_exchange`
- `GET /api/v2/data-exchange/space/{space_id}/export?format=json|csv[&suite_ids=...]`
- `POST /api/v2/data-exchange/space/{space_id}/preview?format=json|csv`
- `POST /api/v2/data-exchange/space/{space_id}/import?format=json|csv` (`Idempotency-Key` required)

REST and MCP share JSON schema v1 / CSV v1, 5 MiB input cap, preview validation, object-level space authorization, escaped preview, atomic writes, and receipts scoped by actor and space. Import creates new IDs and does not transfer version/run history, users, attachments, or secrets. Imported case content is not sent to embedding providers. Read-only collaborator imports are rejected.

All REST routes require JWT and space access. Create/update reject a parent document from another space and serialize parent changes per space to prevent concurrent cycles. MCP exposes the same list, tree, get-by-id, create, update, and delete operations; its list tool supports the REST filters and pagination. MCP also provides text and semantic search, plus link/unlink and list/replace operations for Tech Doc/testcase relationships from either side. Each operation checks access to the requested space or document. Space access allows an active space member or an active company admin in that space's company.

### `app/src/custom_field`
- `GET /api/v2/custom-field/space/{space_id}`
- `GET /api/v2/custom-field/{field_id}`
- `POST /api/v2/custom-field/`
- `PATCH /api/v2/custom-field/{field_id}`
- `DELETE /api/v2/custom-field/{field_id}`
- `POST /api/v2/custom-field/value`
- `GET /api/v2/custom-field/value/{entity_id}`

All definition/value routes require JWT and active access to the same space as the field/entity. Definitions support `required` (default false) for testcase fields. Values must match the configured JSON type/options; changing a definition is rejected when saved values would become invalid. Updating an existing value returns the newly saved value over both REST and MCP. Deleting a definition removes live values, while testcase-version and run snapshots retain their embedded metadata and historical values. MCP provides matching `list_custom_fields`, `create_custom_field`, `update_custom_field`, `delete_custom_field`, `get_custom_field_values`, and `set_custom_field_value` tools.

### `app/src/test_case`
- `GET /api/v2/test-case/space/{space_id}` supports `priority` and repeated `tags` filters (AND semantics) and returns priority and tag labels.
- A non-empty `search` on the case space list uses the trigger-maintained PostgreSQL `simple` full-text vector, ranks title/short name above description/preconditions and steps/expected results, and orders equal ranks by case ID. An exact short-name match also handles hyphenated identifiers such as `TC-123`; a missing short name is treated as no exact match and does not suppress title/full-text results. Whitespace-only input preserves the ordinary list sort. Legacy searchable fields postconditions, external ID, and link remain indexed at the lowest weight. If a document would exceed PostgreSQL's 1 MiB tsvector limit, its vector is retried using the first 8,192 characters of each indexed field so the write can still succeed.
- `GET /api/v2/test-suite/space/{space_id}` requires space access; non-empty `search` ranks suite name above description and breaks ties by suite ID. REST and MCP suite listing use the same service and search semantics.
- `GET /api/v2/test-case/space/{space_id}/tags` returns tag options scoped to the space.
- `GET /api/v2/test-case/suite/{suite_id}` and `/section/{section_id}` require access to the owning suite's space and return cases with priority, tags, and custom-field values loaded in one batch.
- `GET /api/v2/test-case/{testcase_id}` and case create/update responses expose `priority`, `tags`, and current custom-field definitions/values. Space list/search and MCP `search_test_cases` expose the same custom fields for returned cases.
- Create/update accept priority `P0`–`P3` and up to 50 tag labels; create defaults to `P2`. PATCH omission retains tags and `tags: []` clears them.
- New version snapshots record type, priority, and immutable tag labels; legacy version rows remain `NULL` for unknown fields. Restore preserves current values for unknown legacy fields.
- Case create/update accepts `custom_fields: [{field_id, value}]`; create enforces every required testcase field, PATCH omission preserves values, and a supplied array replaces the values atomically with a version snapshot. Detail and list/search reads include metadata and values; list, suite, section, and MCP collection paths batch-load them. The same service path is used by REST and MCP.
- New case versions and run result snapshots store custom-field values with copied field name/type/options/required metadata. Legacy snapshots without this property mean unavailable history, not an empty set. Comparison includes custom-field changes.
- New test-run snapshots include priority and tag labels; pre-SU8 snapshots remain readable with those values unknown.
- `POST /api/v2/test-case/` and `PATCH /api/v2/test-case/{testcase_id}` accept a non-negative nullable estimate; version, restore, duplicate, and run snapshot paths preserve it.
- `POST /api/v2/test-case/{testcase_id}/move` accepts required `{suite_id, section_id}`; nullable `section_id: null` targets the suite's virtual Default section. The shared move service validates same-space suite/section placement and does not create a content version.
- `GET /api/v2/test-case/{testcase_id}/runs` includes linked run timing when available.
- `GET /api/v2/test-case/{testcase_id}/versions`
- `GET /api/v2/test-case/{testcase_id}/versions/{version_id}`
- `GET /api/v2/test-case/{testcase_id}/versions/diff`
- `POST /api/v2/test-case/{testcase_id}/versions/{version_id}/restore`
- `GET/PUT /api/v2/test-case/{testcase_id}/tech-docs`

MCP preserves the legacy `move_test_case(case_id, suite_id=None, section_id=None)` signature, partial-update behavior, and testcase response shape for existing callers. New integrations should use `move_test_case_to_location(case_id, suite_id, section_id)` for explicit placement; both destination arguments are required, and callers must pass `section_id: null` to target the destination suite's virtual Default section. This new tool shares placement validation with the REST move endpoint and does not create a content version.

### `app/src/case_template`
- `GET/POST /api/v2/test-case-template/space/{space_id}` — list/create space-scoped templates.
- `GET/PUT /api/v2/test-case-template/space/{space_id}/{template_id}` — read current content plus at most 10 metadata-only history entries / update metadata and append a content version when fields change.
- `GET /api/v2/test-case-template/space/{space_id}/{template_id}/versions?page=1&page_size=20` — page version metadata (maximum 50 per page).
- `GET /api/v2/test-case-template/space/{space_id}/{template_id}/versions/{version_number}` — read one selected immutable version.
- `POST /api/v2/test-case-template/space/{space_id}/{template_id}/use` — create a new testcase from a selected version, required case title, optional allowlisted field overrides, and bounded typed custom-field values.

REST and MCP tools use the same service and check space access before template lookup or writes. REST mutation bodies and MCP template mutation calls are capped at 1 MiB (MCP retains its separate 8 MiB cap for other tools). Content strings are capped at 32,768 characters each, description at 4,096, serialized template content at 128 KiB, and estimated duration at 0–2,147,483,647 seconds; custom fields are excluded from template content and versions. The `use` operation separately accepts at most 50 typed custom-field values with a 64 KiB serialized cap, validated by the existing testcase creation path against definitions in the same space. A template retains at most 100 immutable versions. Template versions contain only case title, text, preconditions, steps, expected results, postconditions, type, priority, and estimated duration. Template name is separate from case title. The use operation copies values into a new testcase through `TestCaseService.create`; no template reference is stored on a case, so later template updates cannot change existing cases.

REST and MCP Tech Docs create/update/delete require `tech_docs`. Every Tech Doc↔testcase link create/remove/replace operation requires combined `traceability`; every referenced object must remain in the same space before writes begin.

### `app/src/traceability`
- `GET /api/v2/traceability/space/{space_id}/matrix` — scoped requirement/case/latest-result coverage; shared REST/MCP service.
- `GET/PUT /api/v2/tech-doc/{tech_doc_id}/test-cases`
- `GET/POST/DELETE /api/v2/traceability/tech-doc/{tech_doc_id}/test-case/{testcase_id}`

The service owns the many-to-many Tech Doc/Test Case links and rejects cross-space links.

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/src/**/router.py`
