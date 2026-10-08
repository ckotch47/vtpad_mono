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
- На desktop подписи фильтров Test Cases остаются читаемыми; поиск и фильтры продолжают менять выдачу.
- Иконки-действия имеют доступные имена, а при клавиатурной навигации виден фокус.
- Cmd/Ctrl+S сохраняет только активную форму; в поиске и вне формы не перехватывает браузерное действие.
- Esc закрывает верхний диалог; при изменённых данных показывает подтверждение, а во время сохранения не закрывает форму.
- UX1 browser spot-check 2026-10-09: on the desktop Test Cases list, opening a blank create form and pressing Ctrl+S left the form open without creating a record; Esc then closed it. Unsaved-change confirmation, active save on a valid form, in-flight save blocking, search/browser shortcut behavior, and nested-overlay targeting remain unverified. No record was saved.

### 2. Full Functional (основной регресс)

0. Shared list loading (UX2, desktop)
- На cases, suites, runs, plans, bugs и Tech Docs замедлить initial response в QA-среде: скелетон занимает место списка, а доступные search/filter controls остаются видимыми и доступными.
- При обновлении после успешной загрузки проверить, что существующие строки/дерево остаются на месте, а индикатор прогресса не подменяет их начальным скелетоном.
- Для initial request и повторного request проверить controlled failure: показывается ошибка вместо ложного «пусто», Retry повторяет чтение; уже загруженное содержимое при ошибке refetch сохраняется.
- Проверить Retry клавиатурой (Tab/Enter/Space) и доступное объявление loading/error. В сценариях использовать QA fixture или network mock; не сохранять и не менять продуктовые записи.

1. Test Cases
- List: поиск, пагинация, сортировка; на desktop подписи поиска и фильтров не обрезаются, фильтры сохраняют поведение.
- Duplicate: кнопка действия в строке кейса имеет имя `Duplicate <case title>` для accessibility tree.
- Detail: вкладки `Details/Run History`; checklist показывает checks и description, без полей case-only.
- Create/Edit: проверить manual и checklist представления; при type-switch hidden `preconditions`/`expected_results` сохраняются после save и version restore.
- Mixed run: checklist и manual отображают соответствующие метки; snapshot сохраняет type и исходные значения.
- Create: создание нового кейса.
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
- Общий таймер различает календарное прошедшее время и измеренные active/paused intervals. Для старого run отсутствие active/paused tracking не скрывает календарное значение и не выдаёт его за время работы тестировщика; фонового polling и перезагрузки страницы нет.
- Mobile layout не проверяется в текущем roadmap pass по указанию пользователя от 2026-10-09.
- Status transitions: проверка смены статусов/step results (если поддерживается UI).
- Delete/archive (если доступно).

3. Test Plans
- List/Detail открываются.
- Create/Edit/Delete тестового плана.
- Связи с cases/runs корректно отображаются.

4. Test Suites
- List/Detail открываются.
- Create/Edit/Delete (или archive) тестового suite.
- Sections/cases внутри suite: add/remove/rename.
- Sections filter: accessible name search finds nested sections and keeps each matching section's ancestors in tree order; keyboard users can focus/select rows.
- Filtering never changes the selected section. When selection is filtered out, the UI says so and offers “Show selection”; clearing restores the full list.
- No-match state is explicit and can be cleared; long section names remain readable through wrapping or their full accessible name. Verify at desktop width.
- SU5 read-only desktop smoke passed on 2026-10-09: matching query, hidden selected section with “Show selection”, no-match message, and clear restored all 5 sections. Nested sections, keyboard focus, and long-name layout still need manual verification.
- SU6 dialog read-only desktop smoke passed on 2026-10-09: action opens for a case, `Default` and each suite section appear, another destination can be selected, and Cancel closes without changing data. REST move and same-location idempotency, MCP discovery and calls to Default/repeat/restore-source passed on disposable database `vtpad_su6_runtime_20261009`; the fixture returned to its original section. Both REST and MCP rejected a section from another suite in the same space; REST returned 422 for that mismatch and 404 for a foreign-space suite. Keyboard behavior remains to verify.

5. Tech Docs
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

6. Bugs (если включено в текущем контуре)
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
