# Ошибки и ограничения (baseline)

## Что описывает

Известные ограничения и типичные ошибки в текущей кодовой базе.

## Известные ограничения

1. **Нет тестов** — ни unit, ни integration, ни e2e. Регрессии не отслеживаются автоматически.
2. **Raw SQL в сервисах** — при рефакторинге моделей запросы ломаются молча.
3. **CORS `allow_origins=['*']`** — открыт для любого origin.
4. **Нет rate limiting** — уязвим для brute-force.
5. **Access token TTL ~30000 мин** — фактически long-lived token.
6. **Нет миграционной системы** — schema managed externally, нет Aerich/Alembic.
7. **Два монтирования роутеров** — `/api/v1/...` и `/v1/...` (legacy), что может путать.
8. **Нет выделенного API-клиента на фронтенде** — Axios дублируется в компонентах.

Подробный разбор потенциально опасных функций и паттернов — в разделе [Слабые места в коде](code-weaknesses.md).

## Типичные ошибки

| Ошибка | Причина | Где искать |
|---|---|---|
| `500` на фильтрации bugs | Raw SQL с hardcoded column name | `app/src/bug/service.py` |
| В модалке бага не переключается вкладка History | Разный тип `value` у `v-tab` и `v-tabs-window-item` (`number` vs `string`) | `vtpad_front_v2/src/components/bugs/modal/bugsModalHistoryComponentV2.vue` |
| Комментарий в модалке бага не сохраняется | Отсутствует `bug.id` или отправляется пустой HTML (`<p></p>`) | `vtpad_front_v2/src/components/bugs/modal/bugsModalCommentComponent.vue` |
| `403` или лог-ошибка в уведомлениях при отсутствии assigner | Background task пытался создать notification с пустым `assigner_id` | `vtpad_backend/app/src/bug/service.py`, `vtpad_backend/app/src/comments/service.py` |
| `401` после долгого простоя | Access token expired, refresh failed | `app/src/auth/service.py`, Redis |

## Исправленные дефекты

1. `PUT /api/v1/comment/{comment_id}` теперь возвращает `404`, если комментарий не найден, вместо `500`.
2. `POST /api/v1/comment/{bug_id}` теперь возвращает `404`, если bug не существует, до создания комментария.
3. `PATCH /api/v2/bugs/{bug_id}` и `PUT /api/v1/bugs/{bug_id}` теперь сначала проверяют существование бага и возвращают `404`, если id не найден.
4. Обновление бага теперь допускает пустые строковые значения для редактируемых полей и корректно обрабатывает `tags=[]` как очистку тегов.
5. Background tasks для уведомлений теперь пропускают пустой `assigner_id`/`create_user_id` и не падают на UUID conversion.
6. Bugs list filtering now respects `show_closed`; when enabled, `HOLD` and `CLOSED` are no longer excluded by default.

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/src/bug/service.py`
- `vtpad_backend/app/src/common/config.py`
- `vtpad_front_v2/src/stores/app.js`
