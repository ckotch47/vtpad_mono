# Health / Readiness / Observability

## Что описывает

Baseline по мониторингу и метрикам backend'а.

## Preconditions

- Backend запущен.
- Prometheus доступен (в dev-окружении через docker-compose.dev.yml).

## Prometheus metrics

- Endpoint: `GET /metrics` (монтируется `prometheus-fastapi-instrumentator`).
- Собирает: latency, request count, status codes по всем HTTP handlers.

## Health checks

- FastAPI не предоставляет встроенного `/health` в текущей конфигурации.
- В dev-окружении через docker-compose поднимается Grafana + Prometheus для визуализации.

## Observability

- Jaeger код присутствует, но закомментирован (`app/utils/jaeger.py`).
- CProfile код также закомментирован.

## Логи

- Uvicorn stdout/stderr.
- Нет структурированного JSON-логирования.

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/utils/jaeger.py`
- `vtpad_backend/docker-compose.dev.yml`
