# Внешние и инфраструктурные зависимости

## Что описывает

Перечень внешних сервисов, баз данных и библиотек, от которых зависит VTPad.

## Инфраструктура

| Сервис | Версия | Назначение | Где настраивается |
|---|---|---|---|
| PostgreSQL | 14 (prod) / 13.3 (dev) | Основная БД | `docker-compose.yml`, `.env` (`db_*`) |
| Redis | 6 | Кеш, refresh-токены | `docker-compose.yml`, `.env` (`redis_*`) |
| Prometheus | — | Метрики backend | `app/main.py` (Instrumentator) |
| LiteLLM Proxy | `ghcr.io/berriai/litellm:main-latest` | Единый OpenAI-совместимый прокси для локальных LLM через Ollama | `docker-compose.litellm.yaml`, `litellm/config.yaml` |

## Backend зависимости (Python)

| Библиотека | Назначение |
|---|---|
| FastAPI 0.115.5 | Веб-фреймворк |
| Tortoise ORM 0.21.7 | Async ORM для PostgreSQL |
| Pydantic v2 | Валидация данных |
| python-jose + passlib | JWT и хеширование паролей |
| redis (asyncio) | Клиент Redis |
| fastapi-mail | SMTP-уведомления (опционально) |
| prometheus-fastapi-instrumentator | Метрики |

## Frontend зависимости (Node)

| Библиотека | Назначение |
|---|---|
| Vue 3.4 | UI-фреймворк |
| Vuetify 3.5 | Компонентная библиотека |
| Vite 5.1 | Сборка |
| Pinia 2.1 | State management |
| vue-router 4 | Роутинг |
| Axios | HTTP-клиент |
| TipTap v2 | Rich-text редактор |
| TipTap extensions | Table, CharacterCount, CodeBlockLowlight, Dropcursor, Underline, TextAlign, TaskList, Suggestion |
| lowlight v3 + highlight.js | Подсветка синтаксиса в code blocks |
| tippy.js | Поповеры для slash-меню редактора |
| vue-chartjs / Chart.js 4 | Графики |
| MDI font | Иконки |

## Внешние интеграции

- `report_url`, `report_port`, `report_api_hash` — интеграция с внешним report-порталом.
- SMTP (опционально, через `fastapi-mail`) — если `use_mail=1`.
- Ollama (`http://192.168.3.15:11434`) — upstream для LiteLLM моделей в `litellm/config.yaml`.

## Источники в коде

- `vtpad_backend/requirements.txt`
- `vtpad_front_v2/package.json`
- `vtpad_backend/app/main.py`
- `vtpad_backend/.env.example`
- `docker-compose.litellm.yaml`
- `litellm/config.yaml`
