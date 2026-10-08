# Пакет DD4 + BD3 — r4

Дата: 2026-10-08. r4 заменяет DD4 часть r3 и фиксирует точный migration/backfill/compatibility/recovery контракт. На target и disposable copy обнаружены 13,836 bug rows, 6,654 duplicate `(spaces_id, short_name)` groups и 6,908 duplicate `bugsmodel.id` groups; у legacy `id` нет PK/unique index. Дублирующиеся строки одинаковы по остальным полям, но это не создаёт стабильный ключ строки.

## Цель

Сделать новые связи bug↔result однозначными по UUID, идемпотентными и доступными одинаково через REST/MCP; сохранить старые JSON-связи без автоматического переосмысления. Закрыть BD3 межпространственные ошибки Tech Docs и подтвердить их runtime проверками.

## DD4 — новые UUID-связи

1. Добавить `bugsmodel.link_uuid UUID` — новый ключ только для новых операций, не меняя legacy `bugsmodel.id`. В транзакционной v14 migration: добавить колонку nullable; заполнить все `NULL` разными `gen_random_uuid()`; установить `DEFAULT gen_random_uuid()` и `NOT NULL`; создать non-partial unique index/constraint. Проверить отсутствие null/duplicates перед commit. DDL блокирует записи в таблицу до commit, чтобы старые/new writers не оставили строку без UUID.
2. В `BugsModel` объявить `link_uuid` UUID с application default; включить его дополнительно к старому `id` в bug list/detail responses. Существующие маршруты по legacy `id` не переопределять.
3. Создать `test_result_bug_link` с FK на result и `bugsmodel.link_uuid`, unique `(result_id, bug_uuid)`, индексами для обоих направлений и временем создания. Новые link/unlink REST/MCP операции принимают `bug_uuid` (значение `link_uuid`), проверяют доступ пользователя к space run, active status и совпадение пространства; повторная связь идемпотентна.
4. Добавить `linked_bugs` в REST run detail и результат с `{id, short_name, title}`, где `id` — `link_uuid`. Для wire compatibility оставить `linked_bug_ids` массивом как сейчас и добавить `linked_bug_ids_raw` с исходным JSON значением БД (включая NULL, duplicates, ambiguous names). PATCH/MCP update сохраняют legacy JSON и не изменяют UUID links. UI показывает UUID links отдельно, legacy references read-only.
5. Legacy `PATCH linked_bug_ids` валидирует каждое ненулевое short name в space, не создаёт/удаляет UUID links, сохраняет порядок/дубликаты. MCP short-name wrapper работает только при одном совпадении, иначе `409`; REST и MCP UUID операции делят одну service проверку.
6. Quick create принимает UUID `operation_id`, title/text/steps; `space_id` выводится из run. В одной транзакции блокируются run/result/space, создаются bug, UUID link и global receipt `(operation_id, actor_id, result_id, payload_hash, bug_uuid)`. Точный повтор возвращает исходный bug; другой actor/result/body получает `409` без раскрытия исходного bug. Receipt держит UUID tombstone без FK на bug, чтобы штатное удаление bug не блокировалось; retry после удаления возвращает `410`. Уведомление выполняется после commit.
7. Не добавлять unique index на short name и не ремонтировать legacy IDs. Общий generator блокирует space row и выдаёт следующий свободный suffix для standard/quick create. Новые связи используют только `link_uuid`.
8. UI передаёт прежний UUID `operation_id` и body при retry, использует `link_uuid` для выбора/удаления связей, оставляет editor открытым при ошибке и перечитывает run после успеха.
9. MCP и REST используют одинаковые domain services и поля новых link responses. MCP update умеет валидировать legacy поле. Не обходить guards прямыми JSON writes.

## BD3 — Tech Docs security

1. Проверить membership для каждого REST/MCP list/tree/get/create/update/delete; все запросы и ответы остаются ограничены space. DTO обновления не может изменить владельца документа.
2. Parent create/move принимает только документ в том же space; проверка cycle и write сериализуются блокировкой строки space.
3. Legacy foreign parent ID не раскрывается через REST/MCP get/tree/list; недействительный parent выдаётся как `null`, а документ показывается корневым. Конкурентные переносы, которые могли бы создать cycle, проверяются runtime.
4. REST и MCP link/unlink/replace/read traceability требуют доступа к обеим сторонам; общий service повторно проверяет same-space пару, включая unlink. Повреждённые legacy cross-space связи не раскрывают поля или UUID чужого объекта.
5. Выполнить двухпространственную матрицу REST и MCP на двух тестовых users/spaces: CRUD чужого документа, foreign/self/descendant parent, попытка сменить `space_id`, повреждённая parent/link запись, cross-space link/unlink/replace и same-space позитивные сценарии.

## Миграция и ограничения данных

- v14 транзакционно добавляет/backfill-ит `link_uuid`, создаёт link/receipt tables/indexes и записывает ledger. Legacy `linked_bug_ids`, `bugsmodel.id` и short names не меняются; short-name unique index не создаётся.
- Обычный startup migration сериализуется PostgreSQL advisory lock между Uvicorn workers/репликами: второй процесс после ожидания перечитывает ledger и не повторяет DDL.
- До применения выполнить read-only preflight обязательных исходных таблиц, оценить размер таблиц/индексов и подтвердить целевую БД `vtpad_back`. На целевой базе есть 13,836 bug rows, 6,654 duplicate short-name groups и 6,908 duplicate legacy ID groups; repair legacy IDs, short-name unique index и backfill неоднозначных legacy JSON связей запрещены.
- До target apply снять `pg_dump -Fc`, сохранить checksum/path и проверить restore на disposable DB. После successful apply rollback приложения — возврат предыдущего image с сохранением `link_uuid`/таблиц; destructive down migration запрещена после появления новых links.
- На disposable clone проверить fresh apply (каждая row получила уникальный link_uuid, legacy IDs/JSON неизменны), повтор (без изменений), injected SQL failure (нет v14 ledger и частичного DDL), успешный retry; два migration runner одновременно должны записать один ledger row.

## Документация

Обновить `project-docs/docs/` по результатам: API endpoints и MCP tools, run-result flow, модель legacy/new bug links, доступ и ошибки. Отметить DD4/BD3 в `ROADMAP.md` и `plans/roadmap-solutions-r1.md` только после реализации и приемочных проверок.

## Приёмка

- REST/MCP создают/читают/добавляют/удаляют UUID-связь по уникальному `link_uuid` для active same-space bug; foreign space, закрытый run и неавторизованный запрос отклоняются без изменения данных.
- Повтор одного operation_id с идентичным actor/result/body возвращает тот же bug; отличающийся actor/result/body не раскрывает данные и возвращает конфликт; параллельные повторы создают ровно один bug/link.
- Стандартный и quick create сериализуют выдачу short name в пределах space и не выдают уже занятую строку; исторические дубликаты сохраняются неизменными и не препятствуют миграции.
- Старые JSON `linked_bug_ids` (включая `NULL`, дублирующиеся и неоднозначные имена) хранятся без преобразования и доступны через `linked_bug_ids_raw`; `linked_bug_ids` сохраняет array wire contract. Новые UUID-связи отображаются однозначно.
- Tech Docs не выдаёт чужие UUID/content, не изменяет cross-space links, не принимает чужого parent и не создаёт cycles.
- Migration apply/retry/failure recovery, backend/frontend checks и независимые API/security reviews проходят. Runtime-доступ к базе и two-space сценарии подтверждены фактически, а не выводятся из компиляции.

## Вне объёма

- Автоматически создавать bug при каждом failed result без явного действия пользователя.
- Исправлять или переопределять смысл исторических duplicate short name и ambiguous JSON links.
- Применять migration к любой другой/production базе, менять secret/environment configuration или отправлять уведомления во внешние системы в ходе теста.
- Реализовывать Dashboard DD1–DD3; они используют только однозначные UUID links, новые данные, и требуют отдельной метрики/плана.

## Изменяемые области

- `vtpad_backend/app/src/test_run/`, `bug/`, `mcp/tools/test_runs.py`
- `vtpad_backend/app/src/traceability/`, `tech_doc/`, `mcp/tools/tech_docs.py`
- `vtpad_backend/app/src/migration/data/` и `app/migration.py`
- frontend run detail/API service
- `project-docs/docs/`, `ROADMAP.md`, `plans/roadmap-solutions-r1.md`

## Статус

Одобрен пользователем как точная ревизия r4 и реализован. Независимые reviews, backend/frontend проверки, disposable DB recovery/runtime репетиции, apply на target и Docker smoke пройдены. Target backup снят и restore проверен; disposable rehearsal databases удалены. Roadmap отмечен после приемки, изменения готовы к commit.
