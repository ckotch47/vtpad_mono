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
- Серверные write-capabilities: `editItems` управляет cases и sections; `editPads` — suites и plans; `editRuns` — runs и results; `editTags` — tags. `manageBugs` управляет bugs/comments, а `editTechDocs` — Tech Docs; для существующих memberships отсутствующие новые флаги трактуются как `true`.
- `right.readOnly: true` запрещает collaborator любые записи через REST и MCP независимо от остальных флагов. Отсутствующий `readOnly` трактуется как `false`; существующие JSON-права массово не переписываются. Space owner и активный `company_admin` своей company имеют полный write-доступ.
- Traceability требует одновременно права записи в cases и Tech Docs; run bug links требуют права записи в runs и bugs.
- Suite mutations through REST/MCP require `suites`; section mutations require `sections`. Section parents and reorder neighbors are checked against the target suite before any write.
- REST-маршруты и MCP-инструменты Tech Docs проверяют доступ через `check_user_into_space`: активное членство в space или роль активного `company_admin` в company этого space. Создать документ или переместить его под родительский можно только внутри того же space; конкурентные переносы сериализуются, чтобы не допустить циклы в дереве. Повреждённый legacy `parent_id`, который указывает за границу space, скрывается в ответах как `null`.
- Запись Tech Docs требует `tech_docs`; создание, удаление и замена Tech Doc/testcase связей требуют `traceability` (`editItems` + `editTechDocs`). REST и MCP проверяют доступ к объектам, а service проверяет, что пара принадлежит одному space до изменения связи.
- REST section reorder and MCP `sort_sections` check access to the space derived from the target section's suite. An active space member or active `company_admin` in that company can reorder only siblings with the same `suite_id` and `parent_id`; callers cannot supply another suite/space in the request.
- Public run link create/read/revoke requires an active membership row in the run's space and active company membership. Creator and space owner may manage their run link; same-company `company_admin` may do so only with active membership in that space. Public redemption grants access only to the documented allowlisted summary until expiry or revocation; it cannot read or change run results.

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


### Test plans, runs, and results

Collaborator writes to test plans require `plans` (`editPads`). Run creation, metadata, lifecycle transitions, deletion, and public-link rotation/revocation require `runs` (`editRuns`). Result status/comment/duration writes require `results` (`editRuns`). Bug links on results, including legacy references and atomic bug creation, require `run_bug_links`, which combines run and bug write access. REST and MCP enforce the same effective capabilities; `readOnly` disables all of them.


Bug create/update requires `bugs`; transitions to `CLOSED`, `HOLD`, or `REOPEN`, and transitions out of `CLOSED`/`HOLD`, also require the legacy `closeBugs` right. Updating other bug fields without changing a closed/held state does not require `closeBugs`. The server-derived `close_bugs` capability combines `bugs` with `closeBugs` and respects `readOnly`. Tag CRUD requires `tags`; assigning/removing tags from a bug requires both `bugs` and `tags`. Comment writes require `bug_comments` on the parent bug space and keep the existing author-only update/delete rule. The server applies owner and active same-company company-admin bypass and honors `readOnly` for all collaborator writes.
