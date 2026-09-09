# Data Flow

## Что описывает

Основные потоки данных между frontend, backend, БД и Redis в экосистеме VTPad.

## Preconditions

- Пользователь аутентифицирован (access token в заголовке).
- Backend подключен к PostgreSQL и Redis.

## Аутентификация и сессия

1. Пользователь вводит логин/пароль.
2. Backend валидирует credentials через bcrypt.
3. Генерируется JWT access token (длинный TTL ~30000 мин) и refresh token.
4. Refresh token сохраняется в Redis.
5. Frontend хранит оба токена и подставляет `Authorization: Bearer <access>` в каждый запрос.
6. При истечении access token frontend вызывает `POST /auth/refresh` с refresh token.
7. Backend проверяет refresh token в Redis и выдаёт новую пару.

## CRUD доменных сущностей

### Space
- Frontend: `GET /spaces` -> backend query -> PostgreSQL -> JSON response.
- Admin: `POST /admin/company` -> backend -> PostgreSQL.

### Pad -> Run -> RunItem
- Frontend: `POST /pads` -> backend -> Tortoise create.
- Frontend: `POST /runs` -> backend -> Tortoise create + копирование items из pad.
- Frontend: `PATCH /runitems/{id}` -> backend -> update status (pass/fail/skip etc).

### Test Suite -> Test Case linking
- Frontend: search and selection for "existing test cases" in suite detail -> `GET /api/v2/test-case/space/{space_id}?search=...` -> backend -> PostgreSQL -> JSON response with `items`.
- Backend search for test cases matches `title`, `short_name`, `text`, `steps`, `expected_results`, `preconditions`, `postconditions`, `external_id`, and `link`.
- Suite detail has a UI-only `Default` section when the suite has no persisted sections or contains cases without `section_id`. It is built from `GET /api/v2/test-case/suite/{suite_id}` and never calls a section endpoint with a synthetic identifier. Adding a case there keeps `suite_id` and sends `section_id: null`.

### V2 Test Run -> immutable execution history
1. Пользователь выбирает ровно один источник: suite, plan или непустой список test cases.
2. Frontend запрашивает `POST /api/v2/test-run/preview`; backend проверяет принадлежность выбранных сущностей space и то, что все cases активны, затем возвращает состав и `source_hash`.
3. Frontend передаёт этот hash в `POST /api/v2/test-run`. Backend повторно собирает выборку, отклоняет устаревший preview с `409` и в одной транзакции создаёт run и `test_result`.
4. Каждый `test_result` хранит JSON snapshot testcase. Поэтому переименование или последующее редактирование testcase не меняет зафиксированный в run текст.
5. Пока run имеет статус `active`, только результат `not_run` допускает один переход в `passed`, `failed`, `blocked` или `skipped`. Завершённый run не редактируется.
6. Устаревшие результаты без snapshot помечаются в API как legacy: UI может показать текущий testcase для совместимости, но не выдаёт его за историческое состояние.

### Test Case versions and Tech Doc traceability
- При обновлении testcase backend сохраняет следующую версию; restore версии создаёт новую текущую версию, а не переписывает историю.
- Case с результатами в runs при удалении переводится в `deprecated`, чтобы не разрушить историю выполнения.
- Связи Tech Doc <-> Test Case находятся в таблице `tech_doc_test_case_link`: связь уникальна, обе стороны должны принадлежать одному space, а удаление Tech Doc очищает её каскадно.

### Bug
- Frontend: `GET /bugs?space_id=...` -> backend -> raw SQL query (сложные фильтры) -> PostgreSQL.
- Frontend: `POST /bugs` -> backend -> Tortoise create.
- Frontend: `POST /bugs/{id}/comments` -> backend -> separate comments table.

## Uploads
- Frontend: `POST /uploads` (multipart/form-data) -> backend -> сохранение в `./uploads/`.
- Backend: раздача файлов по `/uploads/<filename>`.

## Prometheus metrics
- Backend: `GET /metrics` -> `prometheus-fastapi-instrumentator` -> Prometheus text.

## Источники в коде

- `vtpad_backend/app/src/auth/service.py`
- `vtpad_backend/app/src/common/crypto.py`
- `vtpad_backend/app/src/redis/service.py`
- `vtpad_backend/app/src/space/service.py`
- `vtpad_backend/app/src/pad/service.py`
- `vtpad_backend/app/src/run/service.py`
- `vtpad_backend/app/src/runitems/service.py`
- `vtpad_backend/app/src/test_run/service.py`
- `vtpad_backend/app/src/test_case/service.py`
- `vtpad_backend/app/src/traceability/service.py`
- `vtpad_backend/app/src/bug/service.py`
- `vtpad_backend/app/src/file/router.py`
- `vtpad_backend/app/main.py`
