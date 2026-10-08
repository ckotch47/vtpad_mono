# Section Reordering Package — r2 (MCP parity)

Дата: 2026-10-08. Основа: реализованный REST/UI scope из `plans/section-reordering-package-r1.md` и пользовательское требование предоставлять через MCP все операции, доступные через REST.

## Цель

Добавить через MCP ту же возможность перестановки секций, что доступна через REST, с одинаковыми правилами sibling-группы и авторизации.

## Решение

- Добавить MCP tool `sort_sections` в `vtpad_backend/app/src/mcp/tools/sections.py`.
- Аргументы: `section_id`, `sort_before_id`, `sort_after_id`. Требовать ровно один neighbor ID тем же `SectionSortDto` валидатором, который использует REST.
- Вызвать общий `SectionService.update_sort` с текущим MCP HTTP request, чтобы применялись единые проверки target/neighbor, membership через suite space и транзакционная сериализация.
- Возвращать упорядоченный список siblings в простом JSON-совместимом виде с полями `id`, `name`, `description`, `suite_id`, `parent_id`, `sort`.
- Документировать MCP tool и parity в API index, MCP integration docs, roles/access и roadmap.

## Приёмка

- MCP tool виден в списке инструментов и принимает оба режима: before и after.
- Перестановка корней и дочерних секций сохраняется после повторного чтения; parent и suite не изменяются.
- MCP отклоняет пропущенный neighbor, оба neighbor, self, несуществующую секцию и neighbor из другой suite/parent.
- MCP member/active company admin может сортировать siblings; пользователь без membership получает отказ.
- REST и MCP используют одну общую сервисную реализацию, так что валидация, доступ и транзакционность не расходятся.
- Ответ сериализуется как JSON и содержит обновлённую последовательность siblings.
- Миграции и новые зависимости не требуются.

## Проверка

- Python `py_compile` изменённых MCP/backend файлов и diff review.
- Проверка зарегистрированных MCP tool schemas/списка tools и доступности request context.
- При доступном runtime — выполнить MCP sort и проверить повторное чтение; не перезапускать Docker без отдельной необходимости.

## Согласование

Пользователь одобрил revision r2 перед реализацией.

## Результат реализации

- Добавлен MCP tool `sort_sections`; он создаёт общий `SectionSortDto`, передаёт текущий MCP HTTP request в `SectionService.update_sort` и возвращает JSON-массив siblings с согласованными полями.
- Проверка membership, suite/parent соседства, self-reference и транзакционная сортировка общие с REST.
- Добавлена интеграционная документация MCP; roadmap отмечает SU4 реализованным через REST, MCP и UI.
- `py_compile` и `git diff --check` прошли. Независимое API/MCP review подтвердило цепочку auth/request context и безопасную JSON форму. Runtime список инструментов/HTTP MCP вызов не проверен: backend контейнер не запущен, а локально `fastmcp` отсутствует. Docker не перезапускался.
- Миграций и зависимостей нет.
