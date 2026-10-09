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

## Навигация по пространствам

Глобальный `App.vue` владеет состоянием левой панели пространств. Кнопка-переключатель находится в fixed-позиции поверх содержимого приложения, поэтому остаётся доступной после закрытия панели; кнопка переключает `v-model` drawer без перезагрузки маршрута.

## CRUD доменных сущностей

### Space
- Frontend: `GET /spaces` -> backend query -> PostgreSQL -> JSON response.
- Admin: `POST /admin/company` -> backend -> PostgreSQL.

### Pad -> Run -> RunItem
- Frontend: `POST /pads` -> backend -> Tortoise create.
- Frontend: `POST /runs` -> backend -> Tortoise create + копирование items из pad.
- Frontend: `PATCH /runitems/{id}` -> backend -> update status (pass/fail/skip etc).

### Test Suite -> Test Case linking
- Both `/space/:spaceId/test-suites` and `/space/:spaceId/test-suites/:suiteId` render the same workspace: a searchable, status-filtered, server-paginated flat suite navigator beside the selected suite detail. The route parameter is the selected suite; selecting a row pushes its URL, so direct links and browser Back/Forward restore selection. On narrow viewports the workspace shows the list or detail panel, and the detail provides a return-to-list link. The list query (page, page size, search, status and sort) stays in the URL. This is frontend navigation only; no REST/MCP or database contract changed.
- Case search in suite detail is scoped to the selected section (or unassigned cases in `Default`), matches title/short name case-insensitively, trims surrounding whitespace, and keeps the query when the section changes. Clearable `null` is normalized to an empty string. The visible count reflects matches. Loading, request failure with retry, an empty section, and no matches have distinct states; stale responses from a previous section are ignored.
- Frontend: search and selection for "existing test cases" in suite detail -> `GET /api/v2/test-case/space/{space_id}?search=...` -> backend -> PostgreSQL -> JSON response with `items`.
- Backend case and suite search uses PostgreSQL `simple` full-text vectors maintained by database triggers. Case weights are A=`title`/`short_name`, B=`text`/`preconditions`, C=`steps`/`expected_results`, D=`postconditions`/`external_id`/`link`; suite weights are A=`name`, B=`description`. Non-empty search uses parameterized `websearch_to_tsquery`, orders by rank descending then ID ascending, and applies space, permission, type/status/suite/priority/tag filters before pagination. Empty or whitespace-only search keeps the ordinary list sort. REST and MCP call the shared services; both suite-list transports check access to the requested space.
- Test-case priority is stored as `P0`–`P3` (`P2` by default). Case tags are normalized case-insensitively and scoped to a space; repeated `tags` filters use AND semantics. PATCH omission retains tags, while an empty array clears them.
- New testcase versions store type, priority and immutable tag-label snapshots. Pre-v15 version rows keep those fields `NULL` to represent unknown history. New run results snapshot priority and tag labels alongside the testcase content.
- Suite detail has a UI-only `Default` section when the suite has no persisted sections or contains cases without `section_id`. It is built from `GET /api/v2/test-case/suite/{suite_id}` and never calls a section endpoint with a synthetic identifier. Adding a case there keeps `suite_id` and sends `section_id: null`.
- Reordering sections changes only `sort` within one sibling group (`suite_id` + `parent_id`). UI drag and keyboard Move up/down send one adjacent sibling ID to `PATCH /api/v2/section/sort/{section_id}`; MCP clients call `sort_sections` with the same before/after fields. Both paths use the shared service, which checks membership from the section's suite and rewrites all sibling positions in a transaction. Failed UI requests restore the prior order. No migration is required.

### V2 Test Run -> immutable execution history
1. Пользователь выбирает ровно один источник: suite, plan или непустой список test cases.
2. Frontend запрашивает `POST /api/v2/test-run/preview`; backend проверяет принадлежность выбранных сущностей space, но не ограничивает состав статусом testcase, затем возвращает состав и `source_hash`.
3. Frontend передаёт этот hash в `POST /api/v2/test-run`. Backend повторно собирает выборку, отклоняет устаревший preview с `409` и в одной транзакции создаёт run и `test_result`.
4. Каждый `test_result` хранит JSON snapshot testcase и, если suite и вся цепочка секций принадлежат space кейса, полный путь секций от корня до выбранной секции вместе с suite identity/name и порядком секций. Поэтому редактирование testcase, переименование/перенос секции или последующее изменение дерева не меняет зафиксированный в run текст и группировку. При несогласованном suite/section location-поля не раскрываются. Snapshot-узлы секций имеют `{id, name, sort}`; старые snapshots с одним `section` остаются читаемыми.
5. Пока run имеет статус `active`, только результат `not_run` допускает один переход в `passed`, `failed`, `blocked` или `skipped`. Завершённый run не редактируется.
6. Устаревшие результаты без snapshot помечаются в API как legacy: UI может показать текущий testcase для совместимости, но не выдаёт его за историческое состояние.
7. Run detail группирует results по suite и полному section path. Навигация показывает видимые группы и их счётчики с учётом фильтра; desktop использует соседний sticky список, mobile — горизонтальные кнопки. Переход к группе прокручивает и фокусирует её заголовок. Для старых snapshot без path используется только известная секция; у legacy result текущий путь показывается как compatibility data.

### Case estimates and shared run timer
- `estimated_duration_seconds` хранится в кейсе и версиях; при создании run значение копируется в `testcase_snapshot`, поэтому позднее редактирование или restore кейса не меняет уже созданную историю.
- `TestResultModel.duration_seconds` остаётся фактической длительностью отдельного кейса и редактируется вручную. Сумма run складывает только известные значения и отдельно сообщает число результатов без замера; `NULL` и `0` имеют разный смысл.
- Общий timer run хранит интервалы на сервере: старт run открывает интервал, pause закрывает, resume открывает следующий, complete закрывает открытый интервал. Активное время — сумма интервалов, паузы в него не входят; timer общий для участников и не распределяет время по отдельным тестерам. Фонового цикла/cron нет: API рассчитывает длительности по сохранённым границам при каждом запросе, а UI обновляет показания при загрузке, смене состояния или ручном обновлении.
- REST и MCP предоставляют одинаковые операции lifecycle timer и timing поля; все операции проверяют доступ к space. Старые run без timer intervals сохраняют календарные даты, но активное время и паузы остаются неизвестными.
- Bug links in run results preserve the legacy `linked_bug_ids` JSON value exactly. New links use `test_result_bug_link` with a UUID FK and are returned separately as `linked_bugs`. REST and MCP share the service checks for membership, active run, and same-space bug. Quick-create uses one transaction for bug, link, and idempotency receipt; PostgreSQL space-row locking serializes new short-name allocation without imposing uniqueness on legacy names.

### Test Case versions and Tech Doc traceability
- При обновлении testcase backend сохраняет следующую версию; restore версии создаёт новую текущую версию, а не переписывает историю.
- Case с результатами в runs при удалении переводится в `deprecated`, чтобы не разрушить историю выполнения.
- Связи Tech Doc <-> Test Case находятся в таблице `tech_doc_test_case_link`: связь уникальна, обе стороны должны принадлежать одному space, а удаление Tech Doc очищает её каскадно.
- REST- и MCP-операции Tech Docs проверяют доступ через `check_user_into_space` для списка, дерева, поиска, чтения, создания, обновления и удаления. MCP предоставляет те же CRUD, список с фильтрами и пагинацией, дерево и получение по ID; дополнительно доступны текстовый и семантический поиск и операции просмотра/замены/создания/удаления связей с test cases. При создании или переносе документа родитель должен принадлежать тому же space; создание и удаление, а также переносы сериализуются по space, циклическая иерархия отклоняется.
- При чтении traceability связанная запись выдаётся только если её `space_id` совпадает с `space_id` связи; повреждённые cross-space ссылки не раскрывают поля связанного объекта. При чтении Tech Doc недействительный legacy `parent_id` не раскрывается и сериализуется как `null`; в дереве такой документ показывается корневым.
- REST unlink проверяет доступ к Tech Doc и testcase, а общий `TraceabilityService.unlink` повторно требует same-space пару перед удалением, чтобы REST и MCP сохраняли одинаковый инвариант.

### Bug
- Frontend: `GET /bugs?space_id=...` -> backend -> raw SQL query (сложные фильтры) -> PostgreSQL.
- Frontend: `POST /bugs` -> backend -> Tortoise create.
- Frontend: `POST /bugs/{id}/comments` -> backend -> separate comments table.
- Dashboard: `/api/v2/analytics/space/{space_id}/bugs` and its `/by-run`/`/by-suite` views read only explicit UUID links. Queries check membership and same-space bug/run equality; legacy JSON bug IDs are excluded. Each bug item returns at most 25 result navigation pairs and reports truncation while retaining the full link count.
- Bug details opened from analytics use `/api/v2/bugs/space/{space_id}/by-link/{link_uuid}`; legacy numeric IDs are not used because historical duplicates exist.
- Quality analytics `/api/v2/analytics/space/{space_id}/quality` and time analytics `/api/v2/analytics/space/{space_id}/time` require current space membership before running aggregates; MCP tools call the same service and checks. Completed runs are bucketed by `completed_at` in UTC. Failed-rate denominator includes passed/failed/blocked/skipped, excludes `not_run`, and coverage reports denominator against all results. Recurrent cases are selected independently within each suite from its latest 20 completed runs in the selected date range and link back to run/result IDs. The paginated `/quality/results` REST route and `get_quality_results` MCP tool provide a bounded drill-down for one suite/week with the contributing run/result IDs.
- Historical estimate, actual result duration and case-suite attribution use `testcase_snapshot`; null, deleted or foreign suite IDs are combined into `Unknown / mixed suite` without exposing stored IDs. Actual-duration `NULL` is unmeasured while zero is measured. Active time sums timer intervals only and excludes pauses. Because each run has one shared timer, the whole timer is assigned once to the run's same-space `test_run.suite_id`; a missing/invalid run suite goes into `Unknown / mixed suite` and is never copied to every suite represented by its results. Run interval duration is assigned wholly by the run's completion bucket, without splitting at calendar boundaries.

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
