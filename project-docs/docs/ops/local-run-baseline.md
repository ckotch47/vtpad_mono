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

### Локально (Python)

```bash
cd vtpad_backend
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
- `vtpad_front_v2/package.json`
- `vtpad_front_v2/vite.config.mjs`
