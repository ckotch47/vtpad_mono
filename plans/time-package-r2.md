# Пакет времени TE1–TE5 — r2

Дата: 2026-10-08. Основа: `plans/roadmap-solutions-r1.md`, пункты TE1–TE5. Это точный план следующей реализации; код и миграция БД до согласования этой ревизии не меняются.

## Результат

В кейсе хранится nullable-оценка времени. Результат run хранит фактическое время кейса, а run — календарное и активное время с паузами. История показывает эти показатели раздельно и сохраняется при последующем редактировании кейса.

## Зафиксированные решения

- **Таймер общий для run**, по выбору пользователя от 2026-10-08. Он измеряет активное время всего run за вычетом пауз. Время не атрибутируется отдельным тестерам.
- Нажатие **Start Run** запускает общий таймер. **Pause / Resume** закрывают и открывают серверные интервалы. Завершение run закрывает активный интервал.
- Время кейса в результате — существующее редактируемое `duration_seconds` (фактическое время), не автоматический кейсовый секундомер. Значения вводятся/правятся вручную в этом пакете.
- Все длительности хранятся целым числом секунд: `NULL` означает «нет замера», `0` является валидным значением, отрицательные значения запрещены.
- Нет фонового таймерного цикла, cron-задачи или клиентского секундного интервала: сервер хранит границы интервалов и рассчитывает длительности при API-запросе; UI получает свежие значения при загрузке, переходе состояния и ручном обновлении.
- Функции, появившиеся в REST в этом пакете (таймер, состояние и новые поля), доступны и через MCP. MCP-переходы проверяют доступ к space тем же guard.
- Для истории run snapshot оценки берётся из текущего кейса в момент создания run; оценка также сохраняется в версии кейса и восстанавливается вместе с выбранной версией. Существующие строки не backfill-ятся: их оценка и время таймера остаются неизвестными.

## Объём

1. Добавить `estimated_duration_seconds` в `test_case` и `test_case_version`, Pydantic DTO и ответы списка/деталей/версий/сравнения; учесть create, edit, duplicate и restore; добавить поле в форму редактирования кейса. Добавить nullable поле оценки в testcase snapshot результата и в hash предпросмотра/создания run.
2. Сохранить редактируемое фактическое `TestResultModel.duration_seconds`, валидировать `>= 0` для REST/MCP, показывать `0` отдельно от `NULL` в результате, редакторе и истории.
3. В detail run считать сумму только известных фактических времён кейсов и количества результатов без замера. Не хранить производную сумму отдельно; пересчитывать после изменений.
4. Добавить серверную таблицу интервалов общего таймера run с `started_at`, `ended_at` и актором для аудита переходов; обеспечить не более одного открытого интервала на run. Использовать транзакцию и блокировку строки run при start/pause/resume/complete. Старт run открывает интервал, pause закрывает его, resume открывает следующий, complete закрывает открытый интервал. Время рассчитывается сервером, клиентский счётчик не является источником данных.
5. Расширить REST и MCP контракт: состояние таймера и переходы pause/resume; timing поля detail run и списка истории результата. В UI run показать общий таймер, pause/resume, календарную длительность, активное время, паузы и сумму кейсов с количеством незамеренных. В Run History кейса показывать фактическую длительность кейса и доступные timing данные связанного run.
6. Добавить аддитивную JSON-миграцию текущего механизма; миграция применяется автоматически при старте backend. Обновить `project-docs/docs/` (API, архитектура/flows, migration/deployment notes и ограничения legacy данных).

## Приёмка

- Оценка `NULL`, 0 и положительное число корректно сохраняются в REST/MCP; отрицательное значение отклоняется. Изменение/restore оценки создаёт корректную версию; старый run сохраняет прежний snapshot.
- По run показываются сумма известных фактических длительностей и число неизвестных; `NULL` никогда не выглядит как измеренный 0.
- Состояния таймера переживают перезагрузку страницы и видны всем участникам run. Паузы не добавляют активное время; конкурентные запросы и повторные клики не создают два открытых интервала.
- При завершении run открытый интервал закрыт; активное, паузное и календарное время различимы. Старые run без интервалов показывают «нет данных» для активного времени, не ноль.
- Новые/изменённые timing операции доступны через REST и MCP и ограничены space пользователя.

## Вне объёма

Индивидуальное время по тестерам, автоматический секундомер на каждый testcase, аналитические графики AN1/AN2, импорт/экспорт и перезапуск Docker/применение миграции к рабочей БД.

## Ограничения и порядок применения

Миграции запускаются автоматически при старте backend. В реализации подготовить миграционный файл и код, но не запускать миграцию на пользовательской БД и не перезапускать Docker без отдельного явного подтверждения. Проверки кода выполняются только в рамках разрешений текущих project instructions; этот план не расширяет разрешение на запуск тестов.

## Состояние реализации

Код и документация подготовлены; независимый backend/API review пройден после исправления замечаний по совместимости. Первичные статические проверки (`git diff --check`, `py_compile`, JSON-миграция, ESLint) прошли.

## Runtime evidence — 2026-10-08

- Restored the verified pre-apply backup to a disposable PostgreSQL database and started the current backend image against that clone. Startup applied v13 and v14; the working database was not used for mutations.
- REST passed: estimate `0` and positive values persist; negative estimates and actual durations return 422; a run keeps the estimate snapshot after the source case changes.
- REST passed: actual `NULL`, `0`, and positive durations remain distinct in run detail, aggregate counts, and case history. The total sums measured values and counts unmeasured results.
- REST passed: start → pause → resume → complete closes both intervals correctly; paused seconds do not accrue to active time. Two concurrent Resume requests produced one new open interval. The final state and timing remained available through detail and history reads.
- MCP passed: tool discovery and start/pause/resume/complete, result duration update, and run-result reads operated on the same state as REST.
- No automated test suite exists. Browser smoke on the disposable clone verified Start, Pause, and Complete display the corresponding timer states and final durations; the Resume control remains unverified in browser (REST/MCP resume passed above). The production-like backend/frontend containers remained running; v13/v14 were confirmed present in the target migration ledger by read-only query.
- The disposable backend container, database, and temporary script were removed after validation; the verified backup was retained.
