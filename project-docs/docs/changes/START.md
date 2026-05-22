# START baseline

## Что описывает

Стартовый changelog документации. Фиксирует baseline на момент создания.

## Baseline

- Монорепозиторий создан из двух репозиториев (`vtpad_backend` + `vtpad_front_v2`).
- Удалена история коммитов; начальный коммит `init`.
- Добавлена техническая документация на MkDocs Material.

## Состав документации

- Архитектура: system-overview, codebase-map, data-flow.
- API: service-endpoints-map, backend-modules-endpoints-index.
- Flows: auth-flow, bug-lifecycle, pad-run-lifecycle.
- Интеграции, эксплуатация, правила, ошибки, глоссарий.

## Известные риски

- Документация отражает текущее состояние кода без привязки к конкретному commit range.
- При изменении роутеров или моделей документацию нужно обновлять вручную.
