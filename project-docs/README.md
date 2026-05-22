# project-docs

Техническая документация проекта VTPad на MkDocs.

## Структура

- `docs/` — страницы документации
- `mkdocs.yml` — навигация и конфигурация MkDocs
- `Dockerfile` — multi-stage сборка (MkDocs build -> Nginx runtime)
- `docker-compose.yml` — запуск собранного образа

## Локальный запуск (без volume)

```bash
cd project-docs
docker compose up --build docs
```

Документация будет доступна по адресу: <http://localhost:8000>

## Отдельная сборка образа

```bash
cd project-docs
docker compose build docs
```

## Фоновый запуск

```bash
cd project-docs
docker compose up -d docs
```

## Остановка

```bash
cd project-docs
docker compose down
```
