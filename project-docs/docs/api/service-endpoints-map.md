# Карта сервисов и endpoint'ов

## Что описывает

Эта страница фиксирует baseline endpoint'ов по текущему коду backend.

Здесь указаны маршруты, которые явно видны в коде роутеров.

## Preconditions

- Доступен исходный код `vtpad_backend`.
- Backend монтирует роутеры дважды: через `register_router(..., global_prefix='/api')` и через `app.include_router(...)`.
  - Первый вариант добавляет `/api` к префиксу роутера.
  - Второй вариант — legacy, без `/api`.
- Далее указаны пути с префиксом `/api` как основные.

## Общие правила baseline

- Большинство endpoints защищены `Depends(bearer)` (JWT access token).
- Некоторые endpoints дополнительно требуют `Depends(check_user_into_space)` для авторизации на уровне space.
- Auth endpoints (`/api/v1/auth`) — публичные.

## Operational checks

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/health` | Public | liveness процесса; не проверяет зависимости |
| GET | `/ready` | Public | readiness PostgreSQL и Redis; общий `503` при недоступности или тайм-ауте зависимости |

## `vtpad_backend` — Core API

### Auth

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/auth` | Public | login; возвращает access + refresh tokens |
| POST | `/api/v1/auth/refresh` | Public | refresh token -> новая пара tokens |

### Users

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/user` | Public (deprecated) | регистрация |
| GET | `/api/v1/user` | JWT | текущий пользователь |
| PATCH | `/api/v1/user` | JWT | обновление профиля |
| GET | `/api/v1/user/search/by-mail` | JWT | поиск пользователей по email |

### Spaces

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/space` | JWT | список spaces |
| POST | `/api/v1/space` | JWT | создание space |
| GET | `/api/v1/space/{space_id}` | JWT + space check | детали space, включая effective `capabilities` для текущего пользователя |
| GET | `/api/v1/space/{space_id}/users` | JWT + space check | пользователи space |
| PUT | `/api/v1/space/{space_id}` | JWT + space check | обновление space |
| PUT | `/api/v1/space/{space_id}/user` | JWT + space check + owner / active company admin | добавление активного пользователя той же company; повторный запрос возвращает актуальный список участников |
| DELETE | `/api/v1/space/{space_id}/user/{user_id}` | JWT + space check | удаление пользователя |
| PATCH | `/api/v1/space/{space_id}/user/{user_id}` | JWT + space check + owner / active company admin | явная запись `readOnly`, `manageBugs`, `editTechDocs` и legacy flags; `false` сохраняется как false |
| PUT | `/api/v1/space/{space_id}/user-make-owner/{user_id}` | JWT + space check | назначение владельца |
| DELETE | `/api/v1/space/{space_id}` | JWT + space check | удаление space |
| GET | `/api/v1/space/{space_id}/all_runs` | JWT + space check | все runs space |
| GET | `/api/v1/space/{space_id}/statistic` | JWT + space check | статистика space |
| GET | `/api/v1/space/by-short/{short_name}` | JWT | получение по short name |

### Pads

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/pad/{space_id}` | JWT + space check | список pads |
| GET | `/api/v1/pad/detail/{pad_id}` | JWT | детали pad |
| POST | `/api/v1/pad/{space_id}` | JWT + space check | создание pad |
| PATCH | `/api/v1/pad/{pad_id}` | JWT | обновление pad |
| DELETE | `/api/v1/pad/{pad_id}` | JWT | удаление pad |
| PATCH | `/api/v1/pad/sort/{pad_id}` | JWT | сортировка |

### Pad Folders

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/pad-folder/{space_id}` | JWT + space check | список folders |
| GET | `/api/v1/pad-folder/detail/{folder_id}` | JWT | детали folder |
| POST | `/api/v1/pad-folder/{space_id}` | JWT + space check | создание folder |
| PATCH | `/api/v1/pad-folder/{folder_id}` | JWT | обновление folder |
| DELETE | `/api/v1/pad-folder/{folder_id}` | JWT | удаление folder |

### Runs

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/runs/{pad_id}` | JWT | создание run |
| DELETE | `/api/v1/runs/{run_id}` | JWT | удаление run |
| GET | `/api/v1/runs/items/{run_id}` | JWT | items run |
| GET | `/api/v1/runs/{run_id}` | JWT | детали run |
| GET | `/api/v1/runs/all/{pad_id}` | JWT | все runs pad |
| GET | `/api/v1/runs/filter/{space_id}` | JWT + space check | фильтры |
| GET | `/api/v1/runs/by-filter/{space_id}` | JWT + space check | runs с фильтром |
| PATCH | `/api/v1/runs/{run_id}` | JWT | обновление run |

### Run Items

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| PATCH | `/api/v1/runitems/{item_id}` | JWT | обновление статуса item |

### V2 Test Management

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/test-suite/space/{space_id}` | JWT + space check | paginated list; `search` uses PostgreSQL full-text rank (`name` A, `description` B), with `id` tie-break; `status` supports active, archived, all |
| POST | `/api/v2/test-suite/` | JWT + `suites` capability | creates suite in the target space |
| PATCH | `/api/v2/test-suite/{suite_id}` | JWT + `suites` capability | updates suite in its current space |
| DELETE | `/api/v2/test-suite/{suite_id}` | JWT + `suites` capability | archives suite |
| PATCH | `/api/v2/test-suite/sort/{suite_id}` | JWT + `suites` capability | reorders suites only within the same space |
| GET | `/api/v2/test-plan/space/{space_id}` | JWT + space check | paginated plans; includes `suite_ids`, `case_ids`, stored typed `filters`, and the resolved `case_count` |
| POST | `/api/v2/test-plan/preview-selection` | JWT + space check | validates same-space sources and typed testcase custom-field filters; returns selected count and up to 100 case IDs using the same resolver as saved plans and run creation |
| GET | `/api/v2/test-plan/{plan_id}` | JWT + plan-space check | gets plan configuration after checking space access |
| GET | `/api/v2/test-plan/{plan_id}/cases` | JWT + plan-space check | resolved suite/case union after intersecting priority, all-tags, and typed custom-field filters |
| POST | `/api/v2/test-plan/` | JWT + `plans` capability | creates a plan with optional `suite_ids`, `case_ids`, and `filters` |
| PATCH | `/api/v2/test-plan/{plan_id}` | JWT + `plans` capability | updates supplied source/filter fields; omitted filters remain unchanged and `filters: {}` clears filters |
| DELETE | `/api/v2/test-plan/{plan_id}` | JWT + `plans` capability | deletes the plan after checking access to its space |
| POST | `/api/v2/test-run/preview` | JWT + space check | валидирует ровно один источник run и возвращает состав с suite, root→leaf `section_path` и `source_hash`; source, case content, versions, tags, custom fields и locations читаются в одном PostgreSQL `REPEATABLE READ` snapshot |
| POST | `/api/v2/test-run` | JWT + `runs` capability | создаёт run и self-contained result snapshots для cases любого статуса; атомарный selection snapshot согласован даже если caller не передал optional `source_hash`; устаревший preview возвращает `409` |
| GET | `/api/v2/test-run/space/{space_id}` | JWT + space check | список, поддерживает `search`, `milestone_id`, `environment_id`, `status`; возвращает nullable `created_by` с `{id, username}` и `completed_at` |
| GET | `/api/v2/test-run/{run_id}` | JWT + space check | метаданные run |
| GET | `/api/v2/test-run/{run_id}/detail` | JWT + space check | результаты со suite и `section_path` (root→leaf), snapshot/legacy-признак, run timer и сумма фактических длительностей; `linked_bug_ids` остаётся массивом, `linked_bug_ids_raw` содержит неизменённое legacy JSON (включая `null`), `linked_bugs` содержит новые UUID-связи |
| GET | `/api/v2/test-run/{run_id}/compare/{other_run_id}` | JWT + same-space check | сравнивает два завершённых run по сохранённым testcase snapshots; другой space скрывается как `404`, неполный статус возвращает `422`; сравнение без snapshot помечает неизвестные поля и не читает текущий testcase |
| PATCH | `/api/v2/test-run/{run_id}` | JWT + `runs` capability | обновляет метаданные; статус передаётся отдельным lifecycle endpoint |
| POST | `/api/v2/test-run/{run_id}/public-link` | JWT + `runs` capability and public-link owner/creator/admin check | создаёт или ротирует единственную публичную ссылку; 256-bit token возвращается один раз, TTL 7 дней |
| GET | `/api/v2/test-run/{run_id}/public-link` | JWT + strict active-space membership | возвращает только состояние и даты ссылки, никогда не возвращает token |
| DELETE | `/api/v2/test-run/{run_id}/public-link` | JWT + `runs` capability and public-link owner/creator/admin check | отзывает активную ссылку идемпотентно |
| GET | `/api/v2/test-run/public/shared` | Bearer share token в `Authorization` | публичная ограниченная сводка; одинаковый `404` для неизвестной/истёкшей/отозванной ссылки, `no-store`, без referrer; endpoint закрыт feature flag по умолчанию |
| POST | `/api/v2/test-run/{run_id}/start` | JWT + `runs` capability | переводит run из `draft` в `active` и открывает общий timer interval |
| POST | `/api/v2/test-run/{run_id}/pause` | JWT + `runs` capability | закрывает текущий общий timer interval |
| POST | `/api/v2/test-run/{run_id}/resume` | JWT + `runs` capability | открывает следующий общий timer interval |
| POST | `/api/v2/test-run/{run_id}/complete` | JWT + `runs` capability | атомарно завершает active run, закрывает timer interval и создаёт одно уведомление `RUN_COMPLETED` создателю при наличии `created_by`; payload содержит только `run_id` и route |
| PATCH | `/api/v2/test-run/result/{result_id}` | JWT + `results` capability; `run_bug_links` when changing legacy bug references | меняет статус и детали результата только в active run; фактическая длительность `>= 0`, `NULL` означает «нет замера»; ответ включает массив `linked_bug_ids` и оригинал `linked_bug_ids_raw` |
| POST | `/api/v2/test-run/result/{result_id}/bugs/{bug_uuid}` | JWT + `run_bug_links` capability | идемпотентно связывает result с bug по `link_uuid` в том же space |
| DELETE | `/api/v2/test-run/result/{result_id}/bugs/{bug_uuid}` | JWT + `run_bug_links` capability | удаляет UUID-связь с bug в том же space |
| POST | `/api/v2/test-run/result/{result_id}/bugs/link` | JWT + `run_bug_links` capability | short-name convenience wrapper для UUID-связи; только для active run и ровно одного совпадения, неоднозначность возвращает `409` |
| DELETE | `/api/v2/test-run/result/{result_id}/bugs/link` | JWT + `run_bug_links` capability | short-name convenience wrapper с теми же active-run и ambiguity проверками |
| POST | `/api/v2/test-run/result/{result_id}/bugs` | JWT + `run_bug_links` capability | атомарно создаёт bug и UUID-связь; повторяет результат по `operation_id` при совпадении actor/result/body |
| PATCH | `/api/v2/test-run/result/bulk` | JWT + `results` capability | массово меняет статус результатов одного active run; поддерживает возврат в `not_run` |
| GET | `/api/v2/test-case/space/{space_id}` | JWT + space check | список с фильтрами type/status/suite/priority/tags; при непустом `search` PostgreSQL `simple` full-text rank: title/short_name A, description/preconditions B, steps/expected C, legacy searchable postconditions/external_id/link D; отсутствующий short_name не подавляет совпадение по полному тексту; одинаковый rank упорядочивается по `id`; повторяющиеся `tags` работают как AND; каждое case включает `custom_fields` |
| GET | `/api/v2/test-case/space/{space_id}/tags` | JWT + space check | варианты меток кейсов в space |
| GET | `/api/v2/test-case/suite/{suite_id}` | JWT + suite space check | список кейсов suite с приоритетом, метками и `custom_fields` |
| GET | `/api/v2/test-case/section/{section_id}` | JWT + section suite space check | список кейсов section с приоритетом, метками и `custom_fields` |
| POST | `/api/v2/test-case/` | JWT + space check | создаёт кейс с `priority` (`P0`–`P3`, default `P2`), метками `tags` и optional `custom_fields: [{field_id, value}]`; отсутствующие обязательные значения возвращают `422` |
| GET/POST | `/api/v2/test-case-template/space/{space_id}` | JWT + space check | постранично получает метаданные (без content) или создаёт template; начальный version number — 1 |
| GET/PUT | `/api/v2/test-case-template/space/{space_id}/{template_id}` | JWT + space check | detail содержит текущий content и не более 10 metadata-only history entries; обновление полей добавляет immutable version |
| GET | `/api/v2/test-case-template/space/{space_id}/{template_id}/versions?page=1&page_size=20` | JWT + space check | постранично получает metadata-only версии; page size до 50 |
| GET | `/api/v2/test-case-template/space/{space_id}/{template_id}/versions/{version_number}` | JWT + space check | получает content одной выбранной immutable версии |
| POST | `/api/v2/test-case-template/space/{space_id}/{template_id}/use` | JWT + space check | создаёт новый testcase через `TestCaseService.create`, используя выбранную template version, обязательный title, optional allowlisted overrides и typed custom-field values (до 50 значений / 64 KiB); custom fields валидируются в том же space; существующие cases не связаны с template |
| PATCH | `/api/v2/test-case/{testcase_id}` | JWT + space check | обновляет только явно переданные поля, включая оценку `estimated_duration_seconds >= 0`, priority, tags и `custom_fields`; omission сохраняет values, переданный массив заменяет текущие значения; явный `section_id: null` оставляет кейс в виртуальной секции `Default` |
| POST | `/api/v2/test-case/{testcase_id}/move` | JWT + space check | явно перемещает кейс в тело `{suite_id, section_id}`; оба поля обязательны, `section_id: null` означает виртуальную секцию `Default` указанного suite. Suite и section проверяются в space кейса; чужая/несуществующая ссылка возвращает общий `404`, section другого suite в том же space — `422`. Ответ содержит `id`, `space_id`, `suite_id`, `section_id`; перемещение не создаёт content version. |
| GET | `/api/v2/test-case/{testcase_id}/versions` | JWT + space check | история версий testcase |
| GET | `/api/v2/test-case/{testcase_id}/versions/{version_id}` | JWT + space check | конкретная версия testcase |
| GET | `/api/v2/test-case/{testcase_id}/versions/diff` | JWT + space check | сравнение двух версий |
| POST | `/api/v2/test-case/{testcase_id}/versions/{version_id}/restore` | JWT + space check | создаёт новую текущую версию из выбранной; snapshot включает type, priority, метки и совместимые custom-field values |
| GET | `/api/v2/test-case/{testcase_id}/runs` | JWT + space check | история результата кейса с фактическим временем и доступными timing полями связанного run |
| GET/PUT | `/api/v2/test-case/{testcase_id}/tech-docs` | JWT + `traceability` for writes | получает/заменяет связи testcase с Tech Docs |
| GET/PUT | `/api/v2/tech-doc/{tech_doc_id}/test-cases` | JWT + `traceability` for writes | получает/заменяет связи Tech Doc с test cases |
| GET | `/api/v2/traceability/space/{space_id}/matrix?tech_doc_ids=...` | JWT + `check_user_into_space` | requirement→cases→latest result matrix; omit `tech_doc_ids` for all documents or repeat it to select documents in the space. Foreign/unknown requirement IDs return a generic 404. |
| POST | `/api/v2/traceability/tech-doc/{tech_doc_id}/test-case/{testcase_id}` | JWT + `traceability` capability | создаёт same-space связь Tech Doc и testcase |
| DELETE | `/api/v2/traceability/tech-doc/{tech_doc_id}/test-case/{testcase_id}` | JWT + `traceability` capability | удаляет связь только для same-space пары; service повторяет проверку |

The matrix includes Tech Docs with no testcase links and linked cases with no run result. Coverage counts a testcase as covered when its newest result by `updated_at` has status `passed`, `failed`, `blocked`, or `skipped`; `not_run` and missing results are uncovered. A requirement with no cases has `coverage_percent: null` and state `no_testcases`. Corrupt cross-space link rows are omitted before case/result aggregation. `content_display` escapes Tech Doc rich text so returned content is safe to render as text; it does not preserve HTML formatting.

### Custom Fields

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/custom-field/space/{space_id}` | JWT + space check | definitions по space; `entity_type=testcase` возвращает `required` (по умолчанию `false`) |
| GET | `/api/v2/custom-field/{field_id}` | JWT + field space check | definition после проверки доступа к её space |
| POST | `/api/v2/custom-field/` | JWT + space check | создаёт typed definition; select/multiselect требуют хотя бы один уникальный непустой option; required fields поддерживаются для testcase |
| PATCH | `/api/v2/custom-field/{field_id}` | JWT + field space check | type/options меняются только если текущие значения совместимы; select/multiselect требуют хотя бы один уникальный непустой option; включение required требует заполнения у всех существующих cases |
| DELETE | `/api/v2/custom-field/{field_id}` | JWT + field space check | удаляет definition и live values; testcase-version/run snapshots остаются self-contained |
| POST | `/api/v2/custom-field/value` | JWT + entity space check | typed value; field/entity type, same-space и доступ валидируются общим сервисом; testcase mutation создаёт версию |
| GET | `/api/v2/custom-field/value/{entity_id}` | JWT + entity space check | live values определения; пустой набор разрешён для доступного entity |

Plan filters form a candidate set by unioning suite members with explicit `case_ids`; when both source lists are empty, the candidate set is empty. Then priorities, all selected tags, and typed testcase custom-field predicates intersect it. Scalar custom fields use exact matching; multiselect filters match arrays containing the requested values, while an empty array matches only an empty value; a JSON `null` filter selects cases with no non-null value. REST and MCP preview/count/create use the shared plan resolver. Run creation resolves the saved plan filters in the same transaction snapshot as the testcase and custom-field snapshots.

Testcase detail, list/search, create/update response `custom_fields` содержит definition metadata (`field_id`, `name`, `field_type`, `options`, `required`) и `value`; REST и MCP `search_test_cases` включают ту же структуру. Коллекции загружают значения пакетом. Version snapshots хранят metadata и values; `null` означает legacy version без достоверной истории. Создание/обновление принимает `custom_fields: [{field_id, value}]`; ключ `value` обязателен, а JSON `null` явно очищает необязательное значение. В PATCH omission всего `custom_fields` сохраняет values, переданный массив является полной заменой. Явные `null` в полях PATCH определения игнорируются для совместимости с прежним контрактом.

### V2 Sections

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/section/suite/{suite_id}` | JWT | секции suite |
| GET | `/api/v2/section/suite/{suite_id}/tree` | JWT | дерево секций suite |
| POST | `/api/v2/section/` | JWT + `sections` capability | создаёт секцию в suite; parent должен быть той же suite |
| PATCH | `/api/v2/section/{section_id}` | JWT + `sections` capability | обновляет секцию; parent должен быть той же suite |
| DELETE | `/api/v2/section/{section_id}` | JWT + `sections` capability | удаляет секцию |
| PATCH | `/api/v2/section/sort/{section_id}` | JWT + `sections` capability | body задаёт ровно один `sort_before_id` или `sort_after_id`; neighbor должен быть sibling в той же suite и parent. Возвращает упорядоченный список siblings. Неверный body — 422; self/non-sibling — 422; нет capability — 403. Порядок записывается атомарно. MCP counterpart: `sort_sections` с теми же проверками. |
| GET | `/api/v2/tech-doc/space/{space_id}` | JWT + space check | список Tech Docs в space |
| GET | `/api/v2/tech-doc/space/{space_id}/tree` | JWT + space check | дерево Tech Docs в space |
| GET | `/api/v2/tech-doc/{doc_id}` | JWT + space check | получает документ после проверки доступа к его space |
| POST | `/api/v2/tech-doc/` | JWT + `tech_docs` capability | создаёт документ; родитель должен быть в том же space |
| PATCH | `/api/v2/tech-doc/{doc_id}` | JWT + `tech_docs` capability | обновляет документ; родитель должен быть в том же space, переносы сериализуются по space и не создают циклы |
| DELETE | `/api/v2/tech-doc/{doc_id}` | JWT + `tech_docs` capability | удаляет документ после проверки доступа к его space |

Списки V2 test cases, test suites и test plans также возвращают nullable `created_by` с `{id, username}`. Почта и другие персональные данные автора не включаются.

### Items (Pad Items)

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/items/{pad_id}` | JWT | список items |
| POST | `/api/v1/items/{pad_id}` | JWT | создание item |
| PUT | `/api/v1/items/{item_id}` | JWT | обновление item |
| DELETE | `/api/v1/items/{item_id}` | JWT | удаление item |
| PATCH | `/api/v1/items/{item_id}` | JWT | обновление sort/порядка |

### Bugs

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/bugs` | JWT + `bugs` capability | создание bug |
| GET | `/api/v1/bugs` | JWT | список bugs (с фильтрами) |
| GET | `/api/v1/bugs/detail/{bug_id}` | JWT | детали bug |
| GET | `/api/v1/bugs/detail-short` | JWT | детали по short name |
| GET | `/api/v1/bugs/id/by-short` | JWT (deprecated) | bug id по short name |
| PUT | `/api/v1/bugs/{bug_id}` | JWT + `bugs` capability (deprecated) | обновление bug |
| GET | `/api/v1/bugs/filters` | JWT | доступные фильтры |
| PUT | `/api/v1/bugs/{bug_id}/tag` | JWT + `bugs` and `tags` capabilities | добавление tag к bug |
| DELETE | `/api/v1/bugs/{bug_id}/tag/{tag_id}` | JWT + `bugs` and `tags` capabilities | удаление tag из bug |
| GET | `/api/v1/bugs/state-enum` | JWT | enum статусов |
| GET | `/api/v2/bugs/space/{space_id}/by-link/{link_uuid}` | JWT + space membership | детали bug по стабильному UUID связи; выборка проверяет `bugsmodel.spaces_id` |

### Analytics — linked defects

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/analytics/space/{space_id}/bugs` | JWT + space membership | summary уникальных bugs/связей и страница bug; фильтры `status`, `run_id`, `suite_id` применяются и к summary, и к списку; для каждого bug возвращается максимум 25 пар `result_links`, `result_links_truncated` сообщает об усечении; `link_count` содержит полный счётчик |
| GET | `/api/v2/analytics/space/{space_id}/bugs/by-run` | JWT + space membership | пагинированные уникальные bugs и связи по run |
| GET | `/api/v2/analytics/space/{space_id}/bugs/by-suite` | JWT + space membership | пагинированные уникальные bugs и связи по suite snapshot; legacy/неизвестная suite имеет явную атрибуцию |

### Analytics — quality and time trends

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/v2/analytics/space/{space_id}/quality` | JWT + current space membership | Weekly UTC failed rate by suite for completed runs, recurrent failed cases, optional `suite_id`, inclusive `start_date`/`end_date` (`YYYY-MM-DD`); default is the last 12 complete weeks. The rate returns failed/denominator, total results, not-run count and coverage; `has_data` is true only when at least one measured outcome contributes to a rate. Recurrent-case rows include source run/result IDs; aggregate week drill-down is provided by `/quality/results`. |
| GET | `/api/v2/analytics/space/{space_id}/quality/results` | JWT + current space membership | Paginated source results for one same-space `suite_id` and Monday UTC `week_start`; defaults to contributing statuses (`passed`, `failed`, `blocked`, `skipped`), returns source `run_id`/`result_id`, and supports optional status/page filters. `not_run` is excluded to match the rate denominator. |
| GET | `/api/v2/analytics/space/{space_id}/time` | JWT + current space membership | Estimate, measured result duration, average/coverage and active timer intervals for completed runs. Inclusive date ranges up to 31 days use daily UTC buckets; longer ranges use Monday-based weekly buckets. Optional `suite_id`; default is the last 12 complete weeks. |

The MCP tools `get_quality_trends`, `get_quality_results` and `get_time_trends` call the same analytics service and require active membership in the requested space. MCP dates use inclusive `YYYY-MM-DD` strings. Both transports return the same service payload and hide foreign suite IDs as not found. Historical results with missing/invalid suite snapshots and run timers without a valid `test_run.suite_id` are grouped into non-disclosing `Unknown / mixed suite` output. Recurrent cases require a valid same-space snapshot suite, because legacy rows cannot be attributed safely.

Аналитика читает только `test_result_bug_link` и сопоставляет bug и run в одном space; legacy JSON `linked_bug_ids` в метрики не входит. Статусы сводятся к `OPEN`, `FIXED`, `REOPEN`, `OTHER`.

Параметры фильтра для `GET /api/v1/bugs` включают `q` (поиск по `title` и `short_name`), а также существующие фильтры (`state`, `assigner_id`, `create_user`, `tag`, `external_link`, `create_date*`, `estimate_date*`, `order_*`, `skip`, `limit`).

### Bug Comments

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/comment/{bug_id}` | JWT | список comments |
| POST | `/api/v1/comment/{bug_id}` | JWT + `bug_comments` capability | создание comment |
| PUT | `/api/v1/comment/{comment_id}` | JWT + `bug_comments` capability | обновление comment |
| DELETE | `/api/v1/comment/{comment_id}` | JWT + `bug_comments` capability | удаление comment |

### Tags

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/tag/{space_id}` | JWT + space check | список tags |
| PUT | `/api/v1/tag/{tag_id}` | JWT + `tags` capability | обновление tag |
| POST | `/api/v1/tag/{space_id}` | JWT + `tags` capability | создание tag |
| DELETE | `/api/v1/tag/{tag_id}` | JWT + `tags` capability | удаление tag |

### Testcases

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/testcases/filter/{space_id}` | JWT + space check | фильтрованный список |
| GET | `/api/v1/testcases/{space_id}` | JWT + space check | список (с сортировкой) |
| GET | `/api/v1/testcases/paditem/{paditem_id}` | JWT (deprecated) | по pad item |
| GET | `/api/v1/testcases/detail/{testcase_id}` | JWT | детали |
| GET | `/api/v1/testcases/item/{item_id}` | JWT | по item |
| POST | `/api/v1/testcases` | JWT | создание |
| PATCH | `/api/v1/testcases/{testcase_id}` | JWT | обновление |
| POST | `/api/v1/testcases/image/{testcase_id}` | JWT (deprecated) | загрузка image |
| DELETE | `/api/v1/testcases/image/{testcase_id}/{image_id}` | JWT (deprecated) | удаление image |
| DELETE | `/api/v1/testcases/{testcase_id}` | JWT | удаление |
| GET | `/api/v1/testcases/shortname/{short_name}` | JWT | по short name |

### Testcases RunItem / PadItem

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| PUT | `/api/v1/testcases-paditem/{item_id}/{testcase_id}` | JWT (deprecated) | привязка |
| DELETE | `/api/v1/testcases-paditem/{item_id}/{testcase_id}` | JWT (deprecated) | отвязка |
| PATCH | `/api/v1/testcases-runitem/{element_id}` | JWT | обновление связи run-item -> testcase |

### Checklists

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/checklist/list/{space_id}` | JWT + space check | список |
| GET | `/api/v1/checklist/{checklist_id}` | JWT | детали |
| POST | `/api/v1/checklist/{space_id}` | JWT + space check | создание |
| PATCH | `/api/v1/checklist/{checklist_id}` | JWT | обновление |
| DELETE | `/api/v1/checklist/{checklist_id}` | JWT | удаление |
| GET | `/api/v1/checklist/by-short/{short_name}` | JWT | по short name |

### Files / Uploads

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/file` | JWT | upload avatar |
| POST | `/api/v1/file/image` | JWT | upload image |
| GET | `/api/v1/file/{file_id}` | Public | скачивание файла |

### Notifications

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/notification/stream` | JWT | SSE stream; run completion события отправляются только при актуальном доступе к space |
| GET | `/api/v1/notification/unread-count` | JWT | количество видимых непрочитанных уведомлений; revoked run-space membership исключает событие |
| GET | `/api/v1/notification` | JWT | список видимых уведомлений; `skip` 0..1,000,000, `limit` 1..100 |
| PUT | `/api/v1/notification/{notification_id}/read` | JWT | отметить своё видимое уведомление прочитанным; чужие и недоступные run события не изменяются |
| PUT | `/api/v1/notification/read-all` | JWT | отметить видимые уведомления прочитанными |

MCP подключён по Streamable HTTP на `/api/v1/mcp`; ответы JSON-RPC передаются SSE-событиями, поэтому клиенты должны читать поток до нужного ответа, а не ждать закрытия всего HTTP body. `get_notifications`, `get_unread_notification_count`, `mark_notification_read` и `mark_all_notifications_read` используют те же фильтры/сервисы, что и REST. Создание run completion события доступно через общий `complete_test_run` use case; произвольное создание такого события клиентом не предоставляется.

### News

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/news` | JWT | список news |
| PATCH | `/api/v1/news/read` | JWT | отметить прочитанным |
| GET | `/api/v1/news/unread` | JWT | непрочитанные |

### Reports

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/report/test/list/{space_id}` | JWT + space check | список тестов для отчёта |
| GET | `/api/v1/report/test/detail/{test_id}` | JWT | детали теста для отчёта |

### QA Report

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/qa-report/users` | JWT | пользователи для QA отчёта |
| GET | `/api/qa-report/bug-list` | JWT | список багов для QA отчёта |
| GET | `/api/qa-report/email/recipients/{space_id}` | JWT + доступ к space | активные участники space с адресом для выбора получателей email-отчёта |
| POST | `/api/qa-report/email/preview` | JWT + доступ к space | создаёт ограниченный неизменяемый снимок QA-отчёта с allowlist полей на 24 часа |
| POST | `/api/qa-report/email/send` | JWT + доступ к space + активное SMTP-конфигурирование | вручную отправляет отдельное письмо каждому выбранному активному участнику по snapshot; сверяет подтверждённые UI email с актуальными адресами и использует сохраняемый UI idempotency key |

### Notes

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/notes/{space_id}` | JWT + space check | список notes |
| POST | `/api/v1/notes/{space_id}` | JWT + space check | создание note |
| PATCH | `/api/v1/notes/{note_id}` | — | обновление note |
| DELETE | `/api/v1/notes/{note_id}` | — | удаление note |

### Admin — Company

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/amin/company/list` | JWT | список компаний |
| POST | `/api/v2/amin/company` | JWT | создание компании |
| PUT | `/api/v2/amin/company/{company_id}` | JWT | обновление компании |
| GET | `/api/v2/amin/company/detail/{company_id}` | — | детали компании |

### Admin — Company User Settings

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/company-user/list` | JWT | список пользователей |
| PUT | `/api/v2/company-user/{user_id}` | JWT | обновление пользователя |
| POST | `/api/v2/company-user` | JWT | создание пользователя |
| PUT | `/api/v2/company-user/{user_id}/reset-password` | JWT | сброс пароля |
| DELETE | `/api/v2/company-user/{user_id}` | JWT (hidden) | удаление |

## Legacy non-prefixed routes

В `app/main.py` роутеры дополнительно монтируются через `app.include_router(...)` без `/api`.
Это означает, что все пути выше доступны и без `/api` (например, `/v1/space` вместо `/api/v1/space`).

### Data exchange (v2)

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/data-exchange/space/{space_id}/export?format=json\|csv` | JWT + space access | Возвращает versioned content в поле `content`, без filesystem paths; `suite_ids` ограничивает экспорт указанными suites. |
| POST | `/api/v2/data-exchange/space/{space_id}/preview?format=json\|csv` | JWT + space access | Принимает raw JSON или CSV с соответствующим `Content-Type`; возвращает escaped preview и конфликты до записи. |
| POST | `/api/v2/data-exchange/space/{space_id}/import?format=json\|csv` | JWT + writable space access | Принимает raw JSON или CSV, требует `Idempotency-Key`; весь import выполняется одной транзакцией и не отправляет содержимое кейсов embedding-провайдерам. |

Вход ограничен 5 MiB, 10,000 rows, 5,000 cases и 20 уровнями секций. При `right.readOnly=true` импорт отклоняется; owner и активный company admin сохраняют обход read-only ограничения. MCP использует те же операции и структуру ответа.

### CI/CD webhooks (v2)

| Method | Path | Auth/Access | Notes |
| --- | --- | --- | --- |
| POST | `/api/v2/webhooks/integrations` | JWT; space owner or active same-company admin and active space membership | Creates the integration, explicit run allowlist and external-result mappings. Returns the random credential once. |
| GET | `/api/v2/webhooks/integrations/{integration_id}` | JWT; same lifecycle permission | Returns metadata, hash prefix and scope; never returns the credential. |
| POST | `/api/v2/webhooks/integrations/{integration_id}/rotate` | JWT; same lifecycle permission | Atomically replaces the encrypted credential; returns new secret once. |
| POST | `/api/v2/webhooks/integrations/{integration_id}/revoke` | JWT; same lifecycle permission | Revokes the credential. |
| POST | `/api/v2/webhooks/integrations/{integration_id}/callback` | HMAC-SHA-256 signature | Signed JSON `{"results":[{"external_id":"...","status":"passed|failed|blocked|skipped|not_run","duration_seconds":0,"comment":"..."}]}`. 1 MiB / 1,000 result / 60 per minute limits; signed timestamp window ±300 seconds, unique nonce, integration-scoped idempotency. Only active allowlisted runs and mapped results can be updated. |

The canonical signature message is uppercase method, exact request path, timestamp, nonce, and SHA-256 body digest separated by newlines. Credentials are 32 random bytes encrypted with AES-256-GCM under an HKDF-SHA-256 subkey from a separate `WEBHOOK_ENCRYPTION_KEY`; it must not reuse JWT `SECRET_KEY`. `WEBHOOK_ENCRYPTION_KEY_VERSION` identifies the active key, while `WEBHOOK_ENCRYPTION_KEYS` can hold a JSON version-to-base64 keyring for retained keys. MCP `process_webhook_event` supplies the same signed fields and calls the same use case. Run detail exposes safe result `source` provenance; a manual result edit or bug-link change clears it atomically. The 60/minute limit counts verified signed attempts, including rejected payloads and idempotency conflicts. Invalid-auth failures have a separate cap of 120 per integration per minute; after the cap, invalid-auth attempts receive 429 and do not consume the verified quota. Both journals aggregate only integration/minute/error-code and bounded counts. Request audit records retain only identifiers, outcome/error code and count for 30 days; the redacted failure buckets are retained for 24 hours. Nonces expire after 10 minutes and are cleaned opportunistically on subsequent requests, without a scheduler. Timestamp must be 1–12 ASCII digits; nonce must be 16–128 printable ASCII characters in both REST and MCP.
Lifecycle access returns 404 for integrations outside the caller's active space membership, matching the response for unknown IDs; an unauthorized role within the same space receives 403.

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/src/**/router.py`
