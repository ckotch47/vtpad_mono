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
- `check_user_into_space` — dependency, проверяющая, что пользователь состоит в space.
- Владелец space (`user-make-owner`) — полный доступ.
- Обычные участники space — доступ к pads, runs, bugs в рамках space.

## Защита endpoint'ов

- `Depends(bearer)` — проверка JWT access token.
- `Depends(check_user_into_space)` — проверка членства в space.
- Роль `admin` — через `roles_decorator.py` и `roles_enum.py`.

## Источники в коде

- `vtpad_backend/app/src/common/right_guard.py`
- `vtpad_backend/app/src/admin/roles_decorator.py`
- `vtpad_backend/app/src/admin/roles_enum.py`
- `vtpad_backend/app/src/space/router.py`
