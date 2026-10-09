# UI Regression Full Checklist

## Scope

Полный регрессионный набор для `vtpad_front_v2` в space-контексте.
Базовый URL: `http://localhost:5173`.

Для текущего прохода roadmap пользователь исключил мобильную адаптацию и мобильный smoke 2026-10-09. Приёмка новых UI-изменений выполняется на desktop; не добавлять mobile-only правки и не считать mobile проверки выполненными.

Цель:
- проверить, что ключевые пользовательские сценарии работают end-to-end;
- поймать визуальные/типографические регрессии;
- зафиксировать минимальный набор проверок перед релизом.

## Prerequisites

- Frontend поднят (`npm run dev`).
- Backend/API поднят и отвечает без 5xx.
- Тестовый пользователь валиден.
- Есть рабочий `spaceId` с данными.

## Test Sets

### 1. Smoke (быстрый, обязательный)

1. Auth
- Login валидным пользователем.
- Redirect в `/space`.

2. Core lists
- Открываются и загружаются:
  - `test-cases`
  - `test-runs`
  - `test-plans`
  - `test-suites`
  - `tech-docs`

3. Core details
- Из каждого списка открывается detail-экран первого элемента.
- На detail видны ключевые секции/табы.

4. Network sanity
- Нет `5xx` на базовых endpoints.
- Нет критических frontend-ошибок в runtime.

5. UI sanity
- Основной текст не выходит за диапазон размеров (типографический baseline).
- Нет явных layout-breaks (перекрытия, обрезка ключевых блоков).
- Spaces drawer открывается и закрывается без перекрытия первой строки; пустые имена отображаются как `Unnamed space`, поиск по ним не падает.
- На desktop Spaces toggle находится в зарезервированной общей верхней строке на основных маршрутах. Проверить доступное имя `Open spaces navigation`, видимый клавиатурный фокус, открытие/закрытие pointer и клавиатурой без изменения URL/перезагрузки; при открытом drawer toggle не лежит поверх строк Space. Выполнить на viewport `1276x718` и `904x799`; на длинном Run detail проверить после прокрутки.
- На desktop подписи фильтров Test Cases остаются читаемыми; поиск и фильтры продолжают менять выдачу.
- Иконки-действия имеют доступные имена, а при клавиатурной навигации виден фокус.
- Cmd/Ctrl+S сохраняет только активную форму; в поиске и вне формы не перехватывает браузерное действие.
- Esc закрывает верхний диалог; при изменённых данных показывает подтверждение, а во время сохранения не закрывает форму.
- UX1 desktop browser smoke 2026-10-09: on Test Runs, Ctrl+S in a blank create form left it open without creating a record; Esc closed a clean form. With a temporary unsaved name, Esc showed the discard confirmation; dismissing it kept the form open, and accepting it removed only the draft. The Cancel button is keyboard-focusable and Enter closes the empty form. Valid save, in-flight save blocking, search/browser shortcut behavior, and nested-overlay targeting remain unverified. No run was created.
- Route smoke 2026-10-09: opening `/` redirects to `/company/spaces`, which rendered the authenticated spaces list. The old `/space` destination rendered a blank placeholder and has been removed from root/login/delete-space redirects.

### 2. Full Functional (основной регресс)

0a. Consistent desktop list framing (Cases, Suites, Plans, Runs, Bugs)
- На viewport `1276x718` и `1440x900` сверить одинаковую иерархию: page heading, toolbar с фильтрами и действиями, затем список; нет наложения, обрезанных названий или горизонтального переполнения.
- Проверить, что `ListPageToolbar` не скрывает доменные фильтры: Cases type/status/priority/tags/suite, Suites search/status/sort, Plans/Runs search, Bugs search и filter dialog сохраняют прежнюю выдачу/query behavior.
- Клавиатурой пройти фильтры, primary actions, заголовок записи и каждое row action; ссылки открывают details, действия имеют описательные accessible names и видимый focus.
- В Bugs проверить, что `Create…` — кнопка и открывает тот же draft flow; заголовок bug открывает существующее окно без сохранения.
- В Suites проверить split-pane и URL-backed selection: список слева, выбранная деталь справа; edit/archive доступны отдельными кнопками.
- Проверить loading, initial error, permission-denied и empty/no-match; Retry/Clear доступны только в подходящих состояниях.
- Проверить поиск/фильтры и переход по ссылке без полной перезагрузки страницы; сохранять текущие query/route semantics.
- Эта проверка desktop-only; мобильная верстка и mobile smoke исключены по указанию пользователя.

0. Shared list loading (UX2, desktop)
- На cases, suites, runs, plans, bugs и Tech Docs замедлить initial response в QA-среде: скелетон занимает место списка, а доступные search/filter controls остаются видимыми и доступными.
- При обновлении после успешной загрузки проверить, что существующие строки/дерево остаются на месте, а индикатор прогресса не подменяет их начальным скелетоном.
- Для initial request и повторного request проверить controlled failure: показывается ошибка вместо ложного «пусто», Retry повторяет чтение; уже загруженное содержимое при ошибке refetch сохраняется.
- Проверить Retry клавиатурой (Tab/Enter/Space) и доступное объявление loading/error. В сценариях использовать QA fixture или network mock; не сохранять и не менять продуктовые записи.

1. Empty states (UX3, desktop)
- Cases, suites, plans, runs, bugs and the plan case picker distinguish first-empty from filter/search no-match; Create/Clear actions work with keyboard when shown.
- Run detail distinguishes an empty run snapshot from a status filter with no results.
- Tech Docs distinguishes an empty tree from search no-match; load errors stay distinct and Retry remains keyboard accessible.
- Analytics shows a first-empty state and separates aggregate request failure from zero-valued metrics.
- For cases, suites, plans, runs, bugs, run detail, plan case picker, Tech Docs and analytics, simulate a non-permission error (Retry) and HTTP 403 (permission message, no Retry).
- Role-based Create CTA visibility remains an open manual check: there is no shared frontend capability source yet. Do not interpret currently visible create affordances as permission proof.
- UX3 desktop source review (2026-10-09): common empty-state component and route/request guards were reviewed; case search no-match plus Clear filters was observed in the desktop browser and restored the case list. Controlled error/403, keyboard interaction across all states and read-only role fixtures remain open.
- Mobile implementation and smoke are deferred for this roadmap pass per user instruction.

1. Test Cases
- List: поиск, пагинация, сортировка; на desktop подписи поиска и фильтров не обрезаются, фильтры сохраняют поведение.
- Duplicate: кнопка действия в строке кейса имеет имя `Duplicate <case title>` для accessibility tree.
- Detail: вкладки `Details/Run History`; checklist показывает checks и description, без полей case-only.
- Create/Edit: проверить manual и checklist представления; при type-switch hidden `preconditions`/`expected_results` сохраняются после save и version restore.
- Mixed run: checklist и manual отображают соответствующие метки; snapshot сохраняет type и исходные значения.
- Create: создание нового кейса.
- Case templates (desktop): открыть управление, создать шаблон, выбрать его в списке и обновить content; проверить, что правка добавляет версию, а metadata/content показываются для выбранной версии.
- Case template editor: проверить Ctrl/Cmd+S сохранение активной формы, Esc с подтверждением при dirty draft и блокировку Esc на время сохранения; чистая форма закрывается без подтверждения.
- Create from template: при пустом title выбор шаблона подставляет default title; ранее введённый title сохраняется. Проверить реактивное копирование type, priority, estimate, description и полей содержания, возможность их редактировать и отсутствие перезагрузки страницы.
- Template selector race: во время задержанного GET выбрать шаблон, затем очистить выбор; поздний ответ не должен применить поля или метку шаблона к черновику.
- Create cancellation: выбрать шаблон с задержанным GET, закрыть create dialog и снова открыть его. Проверить, что поздний ответ не меняет новый draft, а selector и Create снова доступны.
- Template isolation: создать кейс из выбранного шаблона, обновить шаблон, затем убедиться, что уже созданный кейс не меняется. Tags и custom-field values остаются обычными полями кейса и не берутся из шаблона.
- Edit: изменение полей + сохранение.
- Duplicate: дублирование.
- Bulk: массовая смена статуса.
- Delete: удаление тестового кейса.

2. Test Runs
- List: поиск, пагинация.
- Create: создание run по suite.
- Detail: открытие карточки run.
- На длинном desktop detail карта групп остаётся закреплённой слева, прокручивается отдельно, показывает текущую группу и подсвечивает её строку.
- Переход к группе мышью и клавиатурой переводит фокус к заголовку; полные имена групп доступны, длинные названия не раздвигают страницу.
- Сводка объединена в одну карточку: прогресс и статусы сверху, замеры времени кейсов/run ниже; `NULL` отображается как отсутствие данных, `0` — как измеренное время.
- Для результата, обновлённого webhook, показывается источник `CI: <integration>`; ручное редактирование результата очищает источник. Проверить на desktop без навигации/перезагрузки страницы.
- Общий таймер различает календарное прошедшее время и измеренные active/paused intervals. Для старого run отсутствие active/paused tracking не скрывает календарное значение и не выдаёт его за время работы тестировщика; фонового polling и перезагрузки страницы нет.
- Mobile layout не проверяется в текущем roadmap pass по указанию пользователя от 2026-10-09.
- Status transitions: проверка смены статусов/step results (если поддерживается UI).
- Delete/archive (если доступно).

3. Run completion notifications (FI7)
- Completing a run notifies only its creator; runs without a creator produce no recipient notification.
- Repeated or concurrent completion requests create one notification, not duplicates.
- The notification contains no run title/status, bug details, or user data; its “Open run” action navigates with Vue Router and marks the item read without a page reload.
- After opening an unread notification, the global unread badge refreshes immediately; “Read all” clears the badge without a page reload.
- If notification loading fails, the page leaves the loading state, shows a retryable inline error, and keeps any already loaded notifications visible.
- If the referenced run is no longer accessible, opening it returns the normal access/not-found state and reveals no run details.
- The unread counter and SSE toast update for `RUN_COMPLETED`; the toast uses generic text and does not disclose run metadata.

4. Test Plans
- List/Detail открываются.
- Create/Edit/Delete тестового плана.
- Связи с cases/runs корректно отображаются.

5. Test Suites
- List/Detail открываются.
- Create/Edit/Delete (или archive) тестового suite.
- Sections/cases внутри suite: add/remove/rename.
- Sections filter: accessible name search finds nested sections and keeps each matching section's ancestors in tree order; keyboard users can focus/select rows.
- Filtering never changes the selected section. When selection is filtered out, the UI says so and offers “Show selection”; clearing restores the full list.
- No-match state is explicit and can be cleared; long section names remain readable through wrapping or their full accessible name. Verify at desktop width.
- SU5 read-only desktop smoke passed on 2026-10-09: matching query, hidden selected section with “Show selection”, no-match message, and clear restored all 5 sections. Nested sections, keyboard focus, and long-name layout still need manual verification.
- SU6 dialog read-only desktop smoke passed on 2026-10-09: action opens for a case, `Default` and each suite section appear, another destination can be selected, and Cancel closes without changing data. REST move and same-location idempotency, MCP discovery and calls to Default/repeat/restore-source passed on disposable database `vtpad_su6_runtime_20261009`; the fixture returned to its original section. Both REST and MCP rejected a section from another suite in the same space; REST returned 422 for that mismatch and 404 for a foreign-space suite. Keyboard behavior remains to verify.

6. Tech Docs
- Tree загружается.
- Поиск в sidebar работает.
- Открытие doc из списка.
- При существующих страницах без выбранной страницы предлагается выбрать страницу или создать страницу; `Create first page` используется только для пустого дерева.
- Пока дерево загружается, показывается loading-состояние; при ошибке загрузки показывается ошибка и доступен Retry, без ложного пустого состояния.
- Иконки create/edit/subpage/delete и меню строки имеют доступные имена и подсказки.
- Меню строки видно при наведении и при клавиатурном фокусе; фокус имеет видимое выделение.
- Edit doc (readonly/edit consistency).
- Create new page + create subpage.
- Rename/Delete page.

Desktop UIX r1 retest (2026-10-09): UIX-001–004 passed on the observed run, spaces drawer, cases list, and Tech Docs with existing pages. The cases search returned matching rows without a full page navigation. Keyboard focus on a Tech Docs row revealed its action menu and a visible focus outline. UIX-005 accessible names are present; pointer-hover tooltip behavior was not manually observed. A successful empty Tech Docs tree and Tech Docs load-error fixture were unavailable. Test Plan detail and the empty Test Runs list opened; the testcase edit form opened but showed an existing 404 toast for tag options. The Bugs detail path had no populated detail fixture; the read-only “Create…” row opens a draft form, which was closed without saving. No testcase, run, plan, bug, or Tech Docs record was saved during this retest.

Desktop UI/UX retest (2026-10-09, before UXN-001 fix): the previous fixed toggle overlapped the Test Cases Tags filter and its inner button lacked an accessible name; the drawer showed “No spaces” while the cases list request returned HTTP 500. Implementation evidence is recorded in the current commit; rerun the viewport and long-page checks above when the local service has usable route data. Data-dependent states and mobile remain outside this check.

Desktop UI/UX execution (2026-10-09, after UXN-001 and list framing changes):
- On the authenticated local app, the Spaces toggle exposes the accessible name `Open spaces navigation`. Keyboard focus reaches it, Enter opens the drawer, and the drawer close control returns to the same Run detail URL. Pointer open/close also worked without route change.
- Run detail showed its group map fixed below the shell while the case list scrolled. Selecting Security moved focus to that group heading and updated the current-group indicator. The displayed calendar elapsed value advanced from `3179h 18m` to `3179h 20m` while the Run URL stayed unchanged; this historical run has no tracked active/paused intervals, so those states were not exercised.
- Cases, Suites, Plans, Runs, and Bugs rendered their common heading/toolbar/list hierarchy with populated data. The Suites detail showed the section list on the left and selected section cases on the right. Cases search for `GET /health` updated the query and matching results in place. Bugs search showed `No matching bugs` for an unmatched query and clearing it restored the list.
- This root-session browser pass used the available `853x820` desktop-app viewport. A parallel source/visual review observed Cases at `1276x718` and Suites/Plans/Runs/Bugs at `1440x900`, but those routes were not all rechecked after the final commit. The full route-by-viewport matrix (`1276x718`, `1440x900`), complete keyboard traversal of each filter/action, error/403/loading fixtures, and mobile remain not_run.
- During the parallel smoke, a blank bug `VHC-1` was accidentally created. The frontend proxy was confirmed to target the backend on port `8000`, whose configured DB was the disposable `vtpad_su6_runtime_20261009`. After confirming the exact empty-title row and that it had no linked results, tags, or comments, that one test row was removed from the disposable DB. No production database was touched.
- Verdict: targeted desktop checks passed; full UI/UX acceptance remains partial until the remaining viewport and keyboard/error-state cases above are exercised.

7. Bugs (если включено в текущем контуре)
- List загрузка.
- Создание бага.
- Открытие modal/detail.
- Обновление статуса/тегов/комментариев.
- Failed result: cancel не отправляет create request и не создаёт link/receipt.
- Failed result: invalid title показывает validation, повтор payload безопасен; явный submit показывает bug и создаёт одну result link.

### 3. Permissions & Access

1. Роль без прав редактирования
- Кнопки create/edit/delete скрыты или disabled.
- Нет обхода через прямой URL.

2. Невалидный токен
- Logout/redirect на auth.
- Нет “полуавторизованных” состояний.

### 4. Negative

1. Пустые состояния
- Пустые списки отображаются корректно.
- Нет критических runtime-ошибок.

2. API failures
- 4xx/5xx показываются корректным уведомлением.
- UI не залипает в loading.

3. Validation
- Required-поля валидируются.
- Ошибки форм читаемы.

### 5. Visual Consistency

1. Typography
- Используется единая шкала из `src/styles/typography.scss`.
- Нет локальных ручных `font-size` в страницах/фичах.

2. Containers
- Единый page-container для index-страниц.
- Таблицы/карточки в одном визуальном паттерне.

3. Editor
- Стиль TipTap задаётся только в `src/components/common/editor/editorComponent.vue`.
- Нет page-level style override редактора.

### 6. Responsive (deferred for current roadmap pass)

Mobile and tablet work and smoke are excluded by the user instruction dated 2026-10-09. The following checks are not part of this roadmap acceptance pass.

1. Desktop (>= 1440)
- Ключевые экраны без горизонтального скролла.

2. Tablet (~1024)
- Sidebar/таблицы/формы не ломаются.

3. Mobile (~375-430)
- Основные экраны доступны и читаемы.

## Automation

Текущий smoke-скрипт:
- `vtpad_front_v2/scripts/ui-regression.mjs`

Запуск:
```bash
cd vtpad_front_v2
node scripts/ui-regression.mjs
```

Артефакты:
- `vtpad_front_v2/playwright-ui-regression/report.json`
- `vtpad_front_v2/playwright-ui-regression/*.png`

## Recommended Execution Policy

1. Каждый PR:
- прогон `lint`, `build`, `ui smoke`.

2. Перед merge в release/dev:
- full functional набор.

3. Перед production deploy:
- full + permissions + responsive.

## Exit Criteria

- Smoke: 100% pass.
- Full functional: нет P0/P1 дефектов.
- Visual consistency: нет явных регрессий типографики/layout.
- Network/API: нет системных 5xx на core endpoints.
