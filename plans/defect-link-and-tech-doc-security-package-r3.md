# Пакет DD4 + BD3 — r3

Дата: 2026-10-08. Этот план superseded r4: migration backfill/locking, совместимый API read model и rollout recovery конкретизированы. r3 сохраняется для истории решения добавить отдельный `link_uuid` после обнаружения 6,908 дублирующихся `bugsmodel.id`.

## Цель

Сделать новые связи bug↔result однозначными по UUID, идемпотентными и доступными одинаково через REST/MCP; сохранить старые JSON-связи без автоматического переосмысления. Закрыть BD3 межпространственные ошибки Tech Docs и подтвердить их runtime проверками.

## DD4 — новые UUID-связи

1. Добавить `bugsmodel.link_uuid UUID NOT NULL` для идентификации каждой bug row независимо от дублирующего legacy `id`. При миграции каждой существующей строке присвоить отдельный UUID; создать unique index на `link_uuid`. Для новых bugs поле генерируется моделью и базой. Не менять legacy `bugsmodel.id`.
2. Добавить таблицу `test_result_bug_link` с FK на result и `bugsmodel.link_uuid`, unique `(result_id, bug_uuid)`, индексами для обоих направлений и временем создания. Новая link/unlink операция принимает `link_uuid`, проверяет доступ пользователя к space run, active status и совпадение пространства; повторная связь идемпотентна.
3. Добавить `linked_bugs` в REST run detail и результат с `{id, short_name, title}` из этой таблицы; `id` — новый `link_uuid`. Существующее поле `linked_bug_ids` оставить как legacy JSON и не менять исторические строки. UI показывает UUID-связанные bug отдельно от legacy строк; новые link/unlink действия используют `link_uuid`.
4. `PATCH linked_bug_ids` оставить для совместимости, но валидировать каждый short name в пространстве run и не создавать/удалять UUID links этим полем. MCP legacy `link_bug_to_result(result_id, bug_short_name)` сохранить как wrapper: работать только при ровно одном совпадении в space, иначе вернуть однозначный conflict; добавить REST/MCP операции по `link_uuid` с одинаковыми условиями.
5. Quick create принимает `operation_id`, title/text/steps; `space_id` всегда выводится из run. В одной транзакции блокируются run/result/space в согласованном порядке, создаётся bug, UUID link и receipt. Таблица receipt имеет глобальный PK operation_id, actor/result/body hash/bug reference. Точный повтор actor+result+payload возвращает исходный bug; несовпадающий повтор отвечает конфликтом без раскрытия первоначального bug. Отправка уведомления происходит только после commit.
6. **Не** добавлять уникальный индекс на `bugsmodel.short_name` или repair duplicate legacy IDs. Для новых bug short name общий генератор блокирует строку space, выбирает свободный следующий suffix выше существующих значений и используется и стандартным create bug, и quick create. `link_uuid`, а не legacy `id` или short name, является ключом новой связи.
7. UI отправляет один UUID `operation_id` на одну попытку quick create, сохраняет тот же UUID и body при retry, использует `link_uuid` для выбора и удаления связей. После ошибки editor остаётся открытым; после успеха run detail загружается заново.
8. MCP и REST используют одинаковые domain services и поля ответов. Не обходить guards прямыми JSON writes в MCP.

## BD3 — Tech Docs security

1. Проверить membership для каждого REST/MCP list/tree/get/create/update/delete; все запросы и ответы остаются ограничены space. DTO обновления не может изменить владельца документа.
2. Parent create/move принимает только документ в том же space; проверка cycle и write сериализуются блокировкой строки space.
3. Legacy foreign parent ID не раскрывается через REST/MCP get/tree/list; недействительный parent выдаётся как `null`, а документ показывается корневым. Конкурентные переносы, которые могли бы создать cycle, проверяются runtime.
4. REST и MCP link/unlink/replace/read traceability требуют доступа к обеим сторонам; общий service повторно проверяет same-space пару, включая unlink. Повреждённые legacy cross-space связи не раскрывают поля или UUID чужого объекта.
5. Выполнить двухпространственную матрицу REST и MCP на двух тестовых users/spaces: CRUD чужого документа, foreign/self/descendant parent, попытка сменить `space_id`, повреждённая parent/link запись, cross-space link/unlink/replace и same-space позитивные сценарии.

## Миграция и ограничения данных

- Новая migration добавляет отдельный уникальный `link_uuid` каждой bug row и создаёт link/operation таблицы; не преобразует `linked_bug_ids`, не исправляет short names/legacy IDs и не создаёт short-name unique index. DDL и migration ledger применяются в одной транзакции.
- Обычный startup migration сериализуется PostgreSQL advisory lock между Uvicorn workers/репликами: второй процесс после ожидания перечитывает ledger и не повторяет DDL.
- До применения выполнить read-only preflight обязательных исходных таблиц, оценить размер таблиц/индексов и подтвердить целевую БД `vtpad_back`. На целевой базе есть 13,836 bug rows, 6,654 duplicate short-name groups и 6,908 duplicate legacy ID groups; repair legacy IDs, short-name unique index и backfill неоднозначных legacy JSON связей запрещены.
- Проверить migration fresh apply, повторный запуск и rollback после искусственной ошибки на disposable базе; на целевой пользовательской базе запускать только после проверки migration backup/recovery по имеющимся процедурам.

## Документация

Обновить `project-docs/docs/` по результатам: API endpoints и MCP tools, run-result flow, модель legacy/new bug links, доступ и ошибки. Отметить DD4/BD3 в `ROADMAP.md` и `plans/roadmap-solutions-r1.md` только после реализации и приемочных проверок.

## Приёмка

- REST/MCP создают/читают/добавляют/удаляют UUID-связь по уникальному `link_uuid` для активного run и same-space bug; неавторизованные, чужие bug/space и закрытый run отклоняются без изменения данных.
- Повтор одного operation_id с идентичным actor/result/body возвращает тот же bug; отличающийся actor/result/body не раскрывает данные и возвращает конфликт; параллельные повторы создают ровно один bug/link.
- Стандартный и quick create сериализуют выдачу short name в пределах space и не выдают уже занятую строку; исторические дубликаты сохраняются неизменными и не препятствуют миграции.
- Старые JSON `linked_bug_ids` (включая `NULL`, дублирующиеся и неоднозначные имена) читаются/сохраняются без преобразования. Новые UUID-связи отображаются однозначно в REST, MCP и UI.
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

Подготовлен для согласования. r2 superseded: disposable rehearsal выявил дубликаты legacy `bugsmodel.id` и отсутствие ключа, на который можно сослаться FK. Код DD4 r1/r2 не закоммичен и не применён к целевой БД.
