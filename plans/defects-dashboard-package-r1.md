# Пакет DD1–DD3 — аналитика связанных дефектов, r1

Дата: 2026-10-08. Зависимость DD4 закрыта коммитом `19d5747` и миграцией v14 на `vtpad_back`.

## Цель

Добавить в существующий dashboard space-уровневую аналитику bug, связанных с run results через однозначную таблицу `test_result_bug_link`. Показать общие количества, status-разбивку, фильтруемый список и агрегацию по run/suite. Сохранить строгую изоляцию по space и различать количество уникальных bug и количество связей.

## Контракт метрик

1. Источник — только `test_result_bug_link` + `bugsmodel.link_uuid` + `test_result`/`test_run`; неоднозначные legacy JSON `linked_bug_ids` не считаются и не преобразуются. В UI показать короткую подсказку, что отчёт включает связи, созданные по UUID.
2. **Bug count** считает разные `link_uuid` один раз на выбранном наборе результатов; **link count** считает пары `(result_id, bug_uuid)`. Один bug, связанный с несколькими results, увеличивает link count, но не общий unique bug count.
3. Статусные группы: `OPEN`, `FIXED`, `REOPEN`; `CLOSED`, `HOLD`, `READY` и любое будущее неизвестное значение входят в `OTHER`. Ответ summary всегда содержит все четыре группы, включая нули.
4. Run-агрегация группирует по run. Suite-атрибуция берёт `testcase_snapshot.suite_id` у каждого result, а для legacy result без snapshot отправляет запись в явную группу `unknown_suite` с `attribution='legacy_missing_snapshot'`; текущая принадлежность testcase не используется, потому что кейс мог быть перемещён после run.
5. Run/suite строки отдельно возвращают `unique_bug_count` и `link_count`. Сумма unique bug по нескольким run/suite может повторять один bug; UI не называет её общей уникальной суммой space.

## Backend и API

Добавить в существующий analytics router endpoints (под глобальным `/api`):

- `GET /api/v2/analytics/space/{space_id}/bugs` — ответ `{summary, items, page, page_size, total}`. Query: `status=OPEN|FIXED|REOPEN|OTHER` (optional), `run_id` (optional UUID), `suite_id` (optional UUID), `page` (default 1), `page_size` (default 25, max 100). Summary отражает весь space до list filters. Item содержит `bug_uuid`, `short_name`, `title`, `status`, `link_count`, и связанные run/result IDs для переходов.
- `GET /api/v2/analytics/space/{space_id}/bugs/by-run` — rows `{run_id, run_name, unique_bug_count, link_count}` с пагинацией и сортировкой по link count убыванию, затем стабильным run ID.
- `GET /api/v2/analytics/space/{space_id}/bugs/by-suite` — rows `{suite_id, suite_name, attribution, unique_bug_count, link_count}`; legacy bucket имеет `suite_id=null`, имя `Unknown / legacy`, `attribution='legacy_missing_snapshot'`.

Каждый handler требует bearer и подтверждённое membership пользователя в `space_id`; run/suite filters сначала проверяются в том же space и не должны позволять различать чужой объект. SQL ограничивает пространство через `test_run.space_id` до агрегаций и joins к bug; не доверяет `suite_id` из query без проверки. Для агрегаций применять параметризованный SQL/ORM с уникальными aggregate counts и стабильной пагинацией. Перед добавлением новых индексов выполнить `EXPLAIN (ANALYZE, BUFFERS)` на целевой форме query и описать решение; существующий `UNIQUE(result_id, bug_uuid)` уже обслуживает поиск по result, индекс bug UUID — обратное направление. Schema migration не добавлять без измеренной необходимости.

## Frontend

В `dashboardComponent.vue` добавить секцию Linked Defects после текущих карточек, не заменяя существующие dashboard блоки:

- summary cards: unique bugs, links, Open, Fixed, Reopen, Other;
- status filter и paginated table с `short_name`, title, status, link count и переходами в bug/run result;
- отдельные tabs/tables “By run” и “By suite”, связывающие строку с существующим run detail или bug list; неизвестная suite отображается как историческая legacy-группа;
- пустое состояние сообщает, что UUID-связей пока нет; ошибка загрузки не выглядит как нулевые данные и позволяет retry;
- смена space/filter сбрасывает страницу и отменяет/игнорирует устаревшие ответы; доступность клавиатуры и мобильное размещение сохраняются.

Обновить `analyticsService.js`, API endpoint map и dashboard flow документацию. В `ROADMAP.md` отметить DD1–DD3 только после приемки.

## Проверки и приемка

1. Backend checks и frontend lint/production build проходят; `git diff --check` чист.
2. Runtime fixtures минимум в двух spaces: чужое пространство не даёт данные; чужие run/suite filters отклоняются без утечки; current space даёт ожидаемую выборку.
3. Fixtures покрывают один bug на нескольких results, каждый из статусов, неизвестный status, null/legacy snapshot, suite snapshot, отсутствие связей, pagination ties и фильтры status/run/suite.
4. Reconciliation: unique counts и link counts каждого ответа сверяются SQL-пересчётом от исходных UUID links. Run/suite breakdown сверяется по тем же result IDs; одинаковый bug в нескольких run не суммируется как один в каждой строке и явно не выдаётся как уникальный общий итог.
5. Query plans зафиксированы на целевой форме запроса; N+1 отсутствует; при реальной необходимости индекс утверждается до schema change отдельной точной ревизией.
6. Обновить `project-docs/docs/` для API, flow и ошибок; независимый API/security review; Docker backend/frontend smoke. После approval точной r1 выполнить один scoped commit.

## Вне объёма

- Автоматически связывать любой failed result без явного действия пользователя.
- Интерпретировать или backfill-ить legacy `linked_bug_ids`.
- Менять существующие space/run/testcase аналитические метрики или добавлять внешние dependencies.
- Добавлять фильтры по датам, assignee, label; переносить аналитику в отдельную страницу.
- Менять статусы Tracker, выкатывать на другие базы или производственные окружения.

## Статус

Подготовлен для согласования. Реализация не начиналась; DD1–DD3 остаются незакрытыми до отдельного approval этой ревизии.
