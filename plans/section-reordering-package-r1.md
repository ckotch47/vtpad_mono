# Section Reordering Package — r1

Дата: 2026-10-08. Основа: SU4 из `plans/roadmap-solutions-r1.md`, `SuiteSectionsPanel.vue`, section sort DTO/service и существующая `vuedraggable` dependency. Это точная ревизия; реализация требует явного согласования пользователя именно для r1.

## Цель

Пользователь может менять порядок секций внутри одного родителя в suite. Перетаскивание не меняет родителя секции и не может создавать циклы или затрагивать другую suite.

## Решение

- Reorder ограничен соседними секциями с одинаковыми `suite_id` и `parent_id`, включая список корневых секций.
- Drag-and-drop меняет только сортировку. Перенос между родителями остаётся отдельным SU6 действием.
- Рядом с drag handle доступны клавиатурные команды Move up / Move down для той же sibling-группы.
- Существующие `SectionModel.sort` и `PATCH /api/v2/section/sort/{section_id}` используются без миграции и новой зависимости.

## Объём

1. В UI сделать сортируемые группы соседей, сохраняя текущую древовидную структуру и выбранную секцию. Нельзя перетащить секцию на другой parent или в другую suite.
2. После drop отправлять `sort_before_id` или `sort_after_id` через `sectionService.sort`; API принимает ровно одно соседнее ID и отклоняет self/несуществующего/несоседнего target.
3. В backend проверить, что target и neighbor принадлежат одной suite и одному parent. Проверить membership пользователя в space suite. Сохранить новый порядок транзакционно без дублирующихся позиций внутри sibling-группы.
4. До ответа показывать optimistic order. При ошибке откатывать UI к серверному порядку, сообщать о причине и позволять повторить действие.
5. Обновить `project-docs/docs/` для sort API и ограничений доступа, отметить SU4 в `ROADMAP.md` и `plans/roadmap-solutions-r1.md` после реализации.

## Приёмка

- Корневые секции и секции внутри одного parent можно переставить drag-and-drop и кнопками клавиатуры.
- Reorder сохраняется после reload; selection остаётся на той же секции.
- Попытка переместить между parent/suite не отправляется из UI и отклоняется сервером при ручном API-вызове.
- API отклоняет отсутствующий neighbor, self-reference и смесь `sort_before_id`/`sort_after_id`.
- В запросе без membership пользователь получает отказ; другой member, имеющий действующий доступ к space, может переставить siblings.
- Позиции после операций уникальны и детерминированы в пределах группы; ошибка БД не оставляет частичного порядка.
- Network failure возвращает исходную последовательность и видимое сообщение.
- No migration and no additional npm package.

## Вне объёма

- Перенос секций между родителями/suites, создание и удаление секций.
- Изменение прав collaborators сверх текущего membership доступа; отдельная политика `editCases` не вводится этим пакетом.
- Поиск по дереву секций (SU5) и перенос test cases (SU6).
- Автоматические browser/e2e тесты, Docker и миграции.

## Проверка

- Backend `py_compile` и diff review для transactional reorder/access guards.
- Frontend ESLint и production build.
- По возможности ручной сценарий sibling reorder, reload и rollback при отключённом запросе.

## Согласование

Эта ревизия включает только SU4. Требуется явное подтверждение пользователя для `plans/section-reordering-package-r1.md`, revision r1.
