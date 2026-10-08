# Пакет DD4 + BD3 — r1

Дата: 2026-10-08. Основа: `plans/roadmap-solutions-r1.md`, run result и Tech Docs REST/MCP реализации. Эта ревизия описывает следующий пакет; кодовые изменения начнутся после явного одобрения именно r1.

## Цель

Сделать связь дефекта с результатом прогона надёжной при создании и выборе существующего bug, с одинаковыми возможностями REST и MCP, и закрыть остаточную security-проверку Tech Docs на изоляцию данных между spaces.

## Текущее состояние

- `TestRunService._serialize_result` уже возвращает `linked_bug_ids`; REST run detail использует этот сериализатор.
- UI создаёт bug отдельным запросом, затем отдельным PATCH обновляет JSON-массив `linked_bug_ids`. Ошибка между запросами оставляет bug без связи; повторный запрос создания может породить дубль.
- `TestResultService.update_result` проверяет членство в space run и активность run, но не проверяет, что каждый переданный bug принадлежит тому же space.
- MCP `link_bug_to_result` изменяет результат напрямую, без проверки членства, состояния run, принадлежности bug и общей сервисной транзакции.
- Tech Docs REST/MCP уже вызывают membership guard; service проверяет same-space parent при create/update и сериализует операции дерева блокировкой space. Независимая security review есть; межпространственные runtime-сценарии остаются непроверенными.

## Объём реализации

1. Ввести общую backend-операцию привязки существующего bug к result. Она проверяет доступ к space run, активность run, существование bug, совпадение bug.space с run.space и идемпотентность связи.
2. Добавить REST endpoint и MCP tool для привязки существующего bug через эту же операцию. MCP должен возвращать те же связанные bug identifiers, что и REST; прямые обходные обновления JSON из MCP убрать.
3. Добавить атомарную операцию create-and-link для quick bug flow: bug создаётся и связывается в одной DB-транзакции с блокировкой результата/run. Запрос принимает клиентский `operation_id`; уникальное ограничение сохраняет результат операции, чтобы повтор после сетевой ошибки возвращал уже созданную связь без второго bug. Добавить нужную миграцию с сохранением старых `linked_bug_ids`.
4. Сохранить проверку bug принадлежности также в обычном PATCH `linked_bug_ids`; этот существующий путь не должен обходить общую same-space политику.
5. Выделять `short_name` без коллизий в одной space при параллельных bug creation. Изменить общий генератор для стандартного create и create-and-link, сериализовать выдачу блокировкой space и добавить составной unique constraint/index после проверки исторических данных.
6. Сохранить контракт `operation_id`: UUID уникален глобально; запись хранит actor, result, нормализованный payload hash и созданный bug. Повтор с тем же actor/result/hash возвращает прежний bug; тот же ключ с другим actor, result или payload даёт конфликт без возврата исходной операции.
7. Перевести UI quick bug flow на атомарный REST endpoint и повторное использование `operation_id` для retry одной попытки. Выбор существующего bug использует endpoint из пункта 2.
8. Сохранить `linked_bug_ids` в ответах run detail и результата, включая legacy `NULL` как пустой массив. Обновить API/MCP, flow, архитектурные, access и error docs.
9. Провести независимую security review Tech Docs REST/MCP и выполнить проверку доступа между двумя spaces: tree/list/get/create/update/delete, parent из другого space, перенос между spaces и связи traceability. Проверить same-space pair в общем unlink service и отдельно во всех REST/MCP маршрутах.
10. Не возвращать foreign `parent_id` из повреждённых legacy записей в REST/MCP get/tree/list; сериализовать недействительного parent как `null` и не отдавать его содержимое.
11. Сохранить ацикличность дерева при конкурентных parent updates: одна блокировка space должна сериализовать проверку и запись, а runtime acceptance покрывает параллельные переносы, которые иначе замкнули бы цикл.
12. Сериализовать миграционный startup между несколькими Uvicorn workers/репликами через PostgreSQL advisory lock: миграционная проверка, DDL и ledger update для transactional/non-transactional миграций не должны гоняться за один и тот же migration name.
13. Исправить найденные security-дефекты до приёмки и повторно проверить все изменения независимым reviewer.

## Вне объёма

- Автоматически создавать bug при каждом failed result без явного действия пользователя.
- Новые метрики dashboard DD1–DD3.
- Изменение политики прав/ролей, формат bug, миграция старого JSON в отдельную таблицу связей.
- Перезапуск Docker или применение миграции к пользовательской базе без явного runtime-окна.

## Приёмка

- Повторная загрузка run detail показывает созданный или выбранный bug.
- Повтор create-and-link с тем же `operation_id` возвращает тот же bug; конкурентные повторы не создают дубль.
- Нельзя связать bug из другого space; результат нельзя изменить в завершённом run; неавторизованный пользователь не может читать или менять чужой result/bug.
- PATCH `linked_bug_ids`, REST link/unlink и MCP link/unlink отклоняют чужие bug и не обходят ту же политику доступа.
- Коллизия short name не возникает при параллельных созданиях; перед unique constraint проверены исторические дубликаты, а существующие значения сохранены.
- Повтор `operation_id` с изменённым actor/result/payload не раскрывает bug и завершается конфликтом.
- REST и MCP используют общую сервисную логику, валидируют одинаковые условия и сериализуют одинаковые поля.
- Существующий bug можно связать повторно без дублирования связи; старые `NULL` и массивы `linked_bug_ids` продолжают читаться.
- Tech Docs cross-space runtime-проверки подтверждают отказ для чужого space и parent, а допустимые same-space операции сохраняют работу.
- Повреждённый legacy parent не раскрывает foreign UUID или содержимое через REST/MCP; конкурентные parent changes не создают цикл.
- Два конкурентных startup процесса сериализуются до проверки migration ledger; второй процесс после lock видит migration уже применённой и не запускает DDL повторно.
- Backend compile/static checks, frontend lint/build, миграция проходит статическую проверку; independent API/security review и `git diff --check` проходят.

## Изменяемые области

- `vtpad_backend/app/src/test_run/` (DTO, service, router, model при необходимости)
- `vtpad_backend/app/src/bug/` (транзакционное создание и уникальная выдача short name)
- `vtpad_backend/app/src/traceability/` (same-space REST unlink)
- `vtpad_backend/app/src/tech_doc/` и `vtpad_backend/app/src/mcp/tools/tech_docs.py` (legacy parent serialization and safe hierarchy updates)
- `vtpad_backend/app/migration.py` (startup migration lock)
- `vtpad_backend/app/src/mcp/tools/test_runs.py`
- `vtpad_backend/app/src/migration/data/` и `app/imports.py`, если потребуется модель
- `vtpad_front_v2/src/components/test-runs/detail/testRunDetailComponent.vue` и run API service
- `project-docs/docs/` по API, потокам, доступу, архитектуре и ошибкам
- `ROADMAP.md`, `plans/roadmap-solutions-r1.md`

## Проверки и ограничения

- Сначала проверить DB/runtime доступность и поддерживаемый способ применения migration; production-like данные не изменять.
- Если локально нет работающей тестовой БД, выполнить доступные статические проверки и явно оставить двух-space/runtime acceptance открытым.
- Автоматических backend/frontend тестовых наборов в проекте сейчас нет; не считать статическую компиляцию доказательством runtime-изоляции.

## Статус

Superseded by `plans/defect-link-and-tech-doc-security-package-r2.md` after read-only preflight found 6,654 duplicate `(spaces_id, short_name)` groups. The r1 unique-index migration and short-name links are unsafe for this target database; no r1 code has been committed or applied.
