# Локальный запуск (baseline)

## Что описывает

Инструкция по локальному запуску backend и frontend для разработки.

## Preconditions

- Установлен Docker и docker-compose (или Python 3.10 + Node 20).
- Доступен `.env` (скопирован из `.env.example`).

## Backend

### Через Docker (рекомендуется)

```bash
cd vtpad_backend
docker-compose -f docker-compose.dev.yml up -d --build
```

Поднимет: PostgreSQL 13.3, Redis 6, Prometheus, Grafana, Jaeger, backend.

Backend доступен на `http://localhost:8000`.

### App-only deployment

Если PostgreSQL и Redis уже подняты отдельно, можно использовать compose только для приложений:

```bash
cd /Users/blant/PycharmProjects/vtpad
docker compose -f docker-compose.app-only.yml up -d --build
```

Поднимет только:
- backend на `http://localhost:8000`
- frontend на `http://localhost:3000`

Для этого варианта `vtpad_backend/.env` должен указывать на доступные внешние `db_host` и `redis_host`, потому что сами PostgreSQL и Redis в compose не стартуют.
Корневой `.env` нужен для подстановки `DOMAIN_EXT` в traefik labels.
Backend в compose читает `vtpad_backend/.env`, смонтированный в контейнер как `/app/.env`.
Образ backend кладет код в `/app/app`, чтобы `uvicorn app.main:app` находил пакет `app` внутри контейнера.

### Локально (Python)

```bash
cd vtpad_backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Убедитесь, что PostgreSQL и Redis запущены локально
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend

```bash
cd vtpad_front_v2
npm install
npm run dev
```

Dev-сервер Vite доступен на `http://localhost:5173`.

## Документация (MkDocs)

```bash
cd project-docs
docker compose up --build docs
```

Доступна на `http://localhost:8000`.

## Источники в коде

- `vtpad_backend/docker-compose.yml`
- `vtpad_backend/docker-compose.dev.yml`
- `docker-compose.app-only.yml`
- `vtpad_front_v2/package.json`
- `vtpad_front_v2/vite.config.mjs`
