# Правила ведения документации

## Общее правило

**При любом изменении кода обязательно обновляй соответствующую документацию в `project-docs/docs/`.**

## Что обновлять при изменениях

| Изменение в коде | Какую документацию обновлять |
|---|---|
| Новый / изменённый endpoint | `api/service-endpoints-map.md`, `api/backend-modules-endpoints-index.md` |
| Изменение DTO / request/response models | `api/service-endpoints-map.md` |
| Изменение auth flow / JWT / permissions | `flows/auth-flow.md`, `rules/roles-and-access.md` |
| Изменение business flow (bug, pad, run) | `flows/bug-lifecycle.md`, `flows/pad-run-lifecycle.md` |
| Новый внешний сервис / библиотека | `integrations/dependencies.md` |
| Изменение архитектуры / data flow | `architecture/system-overview.md`, `architecture/data-flow.md` |
| Новый модуль / сервис | `architecture/codebase-map.md` |
| Исправление известного бага / limitation | `errors/common-errors.md` |
| Изменение терминологии | `glossary/terms.md` |

## Как обновлять

1. Внеси изменения в код.
2. Найди соответствующие `.md` файлы в `project-docs/docs/`.
3. Отредактируй их в том же коммите (или в коммите сразу после кода).
4. Если изменений много — можно отдельным коммитом `docs: update ...`.

## Чего не делать

- Не оставляй документацию неактуальной после изменения кода.
- Не добавляй новые разделы без необходимости; обновляй существующие.
- Не дублируй информацию между файлами без причины.
