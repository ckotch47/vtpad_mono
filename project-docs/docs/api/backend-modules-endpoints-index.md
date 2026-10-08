# Backend Modules Endpoint Index

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
- `PATCH /api/v1/space/{space_id}/user/{user_id}`
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
- `GET /api/v2/analytics/space/{space_id}/bugs`
- `GET /api/v2/analytics/space/{space_id}/bugs/by-run`
- `GET /api/v2/analytics/space/{space_id}/bugs/by-suite`

Linked-defect analytics use explicit UUID links only and require space membership. Bug/run joins enforce the same space. Each bug list item contains at most 25 `result_links`; `link_count` remains the full count and `result_links_truncated` indicates omitted navigation pairs.

### `app/src/comments`
- `GET /api/v1/comment/{bug_id}`
- `POST /api/v1/comment/{bug_id}`
- `PUT /api/v1/comment/{comment_id}`
- `DELETE /api/v1/comment/{comment_id}`

### `app/src/tag`
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
- `GET /api/v2/section/{section_id}`
- `POST /api/v2/section/`
- `PATCH /api/v2/section/{section_id}`
- `DELETE /api/v2/section/{section_id}`
- `PATCH /api/v2/section/sort/{section_id}` — JSON body contains exactly one of `sort_before_id` or `sort_after_id`; neighbor must have the same suite and parent; requires suite space membership; returns ordered siblings.

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
- `get_space_suites` transforms items returned by `TestSuiteService.get_by_space(...)` as dictionaries.
- `create_test_plan` uses Bearer token from `Authorization` header when calling `TestPlanService.create(...)`.
- `duplicate_test_case` uses Bearer token from `Authorization` header when calling `TestCaseService.duplicate(...)`.
- `MCPAuthMiddleware` enforces `text/event-stream; charset=utf-8` on MCP SSE responses.
- Space access checks invoked by MCP tools use `request.state.mcp_authenticated_user_id`, which is populated only by `MCPAuthMiddleware` after API-token validation; REST requests continue to resolve the user from their JWT Bearer token.
- Test-run MCP lifecycle includes `start_test_run`, `pause_test_run`, `resume_test_run` and `complete_test_run`; `get_run_results` returns the same timer and duration aggregates as REST. Testcase MCP create/update/read and result updates expose the estimate and validated actual duration.
- `sort_sections` reorders one section relative to exactly one before/after sibling; it uses the same `SectionSortDto` and `SectionService.update_sort` as REST, and returns JSON siblings with `id`, `name`, `description`, `suite_id`, `parent_id`, `sort`.

### `app/src/test_run`
- `POST /api/v2/test-run/preview`
- `POST /api/v2/test-run`
- `GET /api/v2/test-run/space/{space_id}`
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

Run creation snapshots the selected test cases in the same transaction as the new results. A suite, plan, or explicit case selection can include test cases of any status; source validation is limited to source and space membership. Results can be corrected while their run is active; returning a result to `not_run` clears execution attribution and timestamp. List responses for test runs, test cases, test suites and test plans, as well as testcase detail, include a nullable creator `{id, username}` without email.
Run detail keeps the compatible `linked_bug_ids` field as an array and exposes the original legacy JSON as `linked_bug_ids_raw`, including `NULL`, duplicates, and ambiguous historical short names. New `linked_bugs` rows use `bugsmodel.link_uuid` and return `{id, short_name, title}`; REST and MCP use the same service. Legacy short-name link tools only work when exactly one bug in the run space has that name. Quick create takes a client-generated `operation_id`; matching retries return the original bug, mismatched reuse returns `409`, and retry after deletion of the original bug returns `410`. New bug short names are allocated while holding the space row lock; no uniqueness constraint is imposed on historical short names. Run detail also includes a shared timer summary (`state`, calendar/active/paused seconds and interval count), plus the sum of known case durations and measured/unmeasured result counts. Legacy runs without timer intervals report active and paused duration as unknown. The API calculates timer values from stored interval boundaries on request; there is no cron/background timer loop, and the UI refreshes on load, state changes, or explicit refresh. Estimated testcase duration is versioned and copied into each result snapshot; existing records remain `NULL`. New run snapshots and preview items include `suite_id`, `suite_name`, and the root-to-leaf `section_path` (`id`, `name`, `sort` per section). Existing `section` fields remain; old snapshots without a full path are served with only their known section.

MCP keeps `link_bug_to_result` and `unlink_bug_from_result` data semantics: they add/remove a short name in legacy `linked_bug_ids`. They now require an active run and exactly one matching bug in the run space; a missing match returns `404`, while an ambiguous name or inactive run returns `409`. Consumers that used these tools on draft/completed runs must switch to active runs. New UUID links use `link_bug_uuid_to_result` and `unlink_bug_uuid_from_result`. UUID tools and REST endpoints treat their UUID as `link_uuid`; quick-create returns that value as `bug_uuid`, while nested `bug.id` remains the legacy ID. `create_and_link_bug_to_result` uses the same idempotent operation contract as REST. `update_test_result` validates legacy short-name values against the run space and does not modify UUID links.

### `app/src/tech_doc`
- `GET /api/v2/tech-doc/space/{space_id}`
- `GET /api/v2/tech-doc/space/{space_id}/tree`
- `GET /api/v2/tech-doc/{doc_id}`
- `POST /api/v2/tech-doc/`
- `PATCH /api/v2/tech-doc/{doc_id}`
- `DELETE /api/v2/tech-doc/{doc_id}`

All REST routes require JWT and space access. Create/update reject a parent document from another space and serialize parent changes per space to prevent concurrent cycles. MCP exposes the same list, tree, get-by-id, create, update, and delete operations; its list tool supports the REST filters and pagination. MCP also provides text and semantic search, plus link/unlink and list/replace operations for Tech Doc/testcase relationships from either side. Each operation checks access to the requested space or document. Space access allows an active space member or an active company admin in that space's company.

### `app/src/test_case`
- `GET /api/v2/test-case/space/{space_id}` and `GET /api/v2/test-case/{testcase_id}` expose `estimated_duration_seconds`.
- `POST /api/v2/test-case/` and `PATCH /api/v2/test-case/{testcase_id}` accept a non-negative nullable estimate; version, restore, duplicate, and run snapshot paths preserve it.
- `POST /api/v2/test-case/{testcase_id}/move` accepts required `{suite_id, section_id}`; nullable `section_id: null` targets the suite's virtual Default section. The shared move service validates same-space suite/section placement and does not create a content version.
- `GET /api/v2/test-case/{testcase_id}/runs` includes linked run timing when available.
- `GET /api/v2/test-case/{testcase_id}/versions`
- `GET /api/v2/test-case/{testcase_id}/versions/{version_id}`
- `GET /api/v2/test-case/{testcase_id}/versions/diff`
- `POST /api/v2/test-case/{testcase_id}/versions/{version_id}/restore`
- `GET/PUT /api/v2/test-case/{testcase_id}/tech-docs`

MCP preserves the legacy `move_test_case(case_id, suite_id=None, section_id=None)` signature, partial-update behavior, and testcase response shape for existing callers. New integrations should use `move_test_case_to_location(case_id, suite_id, section_id)` for explicit placement; both destination arguments are required, and callers must pass `section_id: null` to target the destination suite's virtual Default section. This new tool shares placement validation with the REST move endpoint and does not create a content version.

### `app/src/traceability`
- `GET/PUT /api/v2/tech-doc/{tech_doc_id}/test-cases`
- `GET/POST/DELETE /api/v2/traceability/tech-doc/{tech_doc_id}/test-case/{testcase_id}`

The service owns the many-to-many Tech Doc/Test Case links and rejects cross-space links.

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/src/**/router.py`
