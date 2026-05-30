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

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/src/**/router.py`
