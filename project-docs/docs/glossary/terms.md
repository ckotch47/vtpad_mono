# Термины

## Что описывает

Базовый словарь технических терминов, используемых в проекте VTPad.

## Термины

- `Space` — проект / рабочее пространство, в рамках которого создаются pads, runs и bugs.
- `Pad` — тест-план / коллекция тестовых элементов (items, testcases, checklists).
- `Run` — прогон (execution) pad'а; фиксирует статус прохождения каждого item'а.
- `Item` — элемент тест-плана внутри pad; может быть ссылкой на testcase или checklist.
- `Bug` — дефект / issue, привязанный к space; имеет статус, priority, assignee.
- `Testcase` — структурированный тест со steps и expected result.
- `Checklist` — список проверок с boolean-статусом.
- `Company` — верхнеуровневая сущность мультиарендности (multi-tenancy).
- `UserCompanySettings` — настройки пользователя внутри company (роль, права).
- `Tortoise ORM` — используемый async ORM для PostgreSQL.
- `FastAPI` — веб-фреймворк backend'а.
- `Vue 3 / Vuetify 3` — фронтенд-стек.
- `Pinia` — state-management на фронтенде.
- `Redis` — кеш и хранилище refresh-токенов.
- `JWT` — механизм авторизации (access token).

## Нормализация имен в документации

- Используем `vtpad_backend` как каноничное имя backend API.
- Используем `vtpad_front_v2` как каноничное имя frontend SPA.

## Источники в коде

- `vtpad_backend/app/src/common/models.py`
- `vtpad_backend/app/src/space/model.py`
- `vtpad_backend/app/src/pad/model.py`
- `vtpad_backend/app/src/run/model.py`
- `vtpad_backend/app/src/bug/model.py`
- `vtpad_backend/app/src/testcases/model.py`
- `vtpad_backend/app/src/checklist/model.py`
- `vtpad_front_v2/src/stores/app.js`
