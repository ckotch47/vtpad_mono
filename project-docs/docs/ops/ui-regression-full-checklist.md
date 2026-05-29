# UI Regression Full Checklist

## Scope

Полный регрессионный набор для `vtpad_front_v2` в space-контексте.
Базовый URL: `http://localhost:5173`.

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

### 2. Full Functional (основной регресс)

1. Test Cases
- List: поиск, пагинация, сортировка.
- Detail: вкладки `Details/Run History`.
- Create: создание нового кейса.
- Edit: изменение полей + сохранение.
- Duplicate: дублирование.
- Bulk: массовая смена статуса.
- Delete: удаление тестового кейса.

2. Test Runs
- List: поиск, пагинация.
- Create: создание run по suite.
- Detail: открытие карточки run.
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

5. Tech Docs
- Tree загружается.
- Поиск в sidebar работает.
- Открытие doc из списка.
- Edit doc (readonly/edit consistency).
- Create new page + create subpage.
- Rename/Delete page.

6. Bugs (если включено в текущем контуре)
- List загрузка.
- Создание бага.
- Открытие modal/detail.
- Обновление статуса/тегов/комментариев.

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

### 6. Responsive

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
