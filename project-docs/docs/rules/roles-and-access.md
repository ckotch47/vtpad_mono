# Роли и доступы (baseline)

## Что описывает

Базовая модель авторизации в VTPad.

## Preconditions

- Пользователь аутентифицирован (JWT access token).

## Уровни доступа

### Global
- `main_admin_id` — супер-администратор (UUID из env).
- Обычные пользователи — регистрация через `POST /api/v1/user`.

### Company
- `UserCompanySettings` — роль пользователя внутри company.
- Admin routes (`/api/v2/amin/company`, `/api/v2/company-user`) доступны для администраторов company.

### Space
- `check_user_into_space` — dependency, проверяющая активное членство пользователя в company целевого space и его membership либо роль `company_admin` в этой же company.
- Владелец space (`user-make-owner`) — полный доступ.
- Изменять участников и настройки space может его владелец или активный `company_admin` той же company. Проверка не зависит от наличия у company admin отдельной записи участника.
- Добавляемый участник должен быть активным пользователем той же company, что и space; иначе API отвечает тем же `404 user not found`, что и для неизвестного email.
- Обычные участники space — доступ к pads, runs, bugs в рамках space.
- REST-маршруты и MCP-инструменты Tech Docs проверяют доступ через `check_user_into_space`: активное членство в space или роль активного `company_admin` в company этого space. Создать документ или переместить его под родительский можно только внутри того же space; конкурентные переносы сериализуются, чтобы не допустить циклы в дереве. Повреждённый legacy `parent_id`, который указывает за границу space, скрывается в ответах как `null`.
- REST и MCP unlink для Tech Doc/testcase требуют доступ к обоим объектам; traceability service повторно проверяет, что пара принадлежит одному space до изменения связи.
- REST section reorder and MCP `sort_sections` check access to the space derived from the target section's suite. An active space member or active `company_admin` in that company can reorder only siblings with the same `suite_id` and `parent_id`; callers cannot supply another suite/space in the request.

## Защита endpoint'ов

- `Depends(bearer)` — проверка JWT access token.
- `Depends(check_user_into_space)` — проверка членства в space.
- Роль `admin` — через `roles_decorator.py` и `roles_enum.py`.
- Проверки роли не должны записывать JWT payload, email, идентификаторы компании или срок токена в application logs.

## Источники в коде

- `vtpad_backend/app/src/common/right_guard.py`
- `vtpad_backend/app/src/admin/roles_decorator.py`
- `vtpad_backend/app/src/admin/roles_enum.py`
- `vtpad_backend/app/src/space/router.py`
