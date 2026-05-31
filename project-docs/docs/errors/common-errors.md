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
| `401` после долгого простоя | Access token expired, refresh failed | `app/src/auth/service.py`, Redis |
| `403` на space endpoints | Пользователь не добавлен в space | `app/src/common/right_guard.py` |
| `404` на uploads | Файл отсутствует в `./uploads` | `vtpad_backend/uploads/` |
| Frontend не подключается к API | Неверный `VITE_API_BASE_URL` | `vtpad_front_v2/.env` |

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/src/bug/service.py`
- `vtpad_backend/app/src/common/config.py`
- `vtpad_front_v2/src/stores/app.js`
