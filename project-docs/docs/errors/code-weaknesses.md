# Слабые места в коде (Code Weaknesses)

## Что описывает

Список потенциально опасных или проблемных функций и паттернов в текущей кодовой базе. Не только «голый SQL», а конкретные места с рисками.

## Preconditions

- Baseline на момент текущего кода.
- Список составлен по статическому анализу; для подтверждения эксплуатации требуется ручная проверка.

---

## Backend

### 1. SQL-инъекции через f-string в raw SQL

**Уровень:** Критический  
**Где:** Почти во всех `service.py`, использующих `execute_query_dict`  
**Проблема:** Переменные подставляются напрямую в SQL через f-string, без параметризации.  
**Статус:** Исправлено — все f-string SQL запросы переведены на параметризованные (`$1`, `$2` и список параметров). Динамические `IN (...)` заменены на `= ANY($n)`. `ORDER BY` и имена столбцов валидируются через whitelist.

| Файл | Строка | Пример уязвимого кода |
|---|---|---|
| `bug/service.py` | 114 | `f"WHERE spaces_id = '{b_filter.space_id}'"` |
| `bug/service.py` | 199 | `f"WHERE bugsmodel.id = '{bug_id}'"` |
| `bug/service.py` | 472 | `f"SELECT * FROM tagmodel WHERE tagmodel.space_id = '{space_id}'"` |
| `bug/service.py` | 518 | `f"WHERE bugsmodel.id = '{bug_id}'"` |
| `runitems/service.py` | 72 | `f"SELECT * FROM runmodel WHERE id='{run_id}'"` |
| `spacesuser/service.py` | 49 | `f"WHERE runmodel.id='{run_id}'"` |
| `testcases/service.py` | 29 | `f"SELECT short_name FROM spacemodel WHERE id = '{space_id}'"` |
| `admin/company/service.py` | 14 | `f"WHERE name LIKE '%{dto.q}%'"` |
| `admin/roles_decorator.py` | 26 | `f"SELECT * FROM usercompanysettingsmodel WHERE user_id = '{user_payload.get('id')}'"` |
| `notification/service.py` | 10 | `f"WHERE user_id = '{dto.user_id}'"` |
| `migration.py` | 44 | `f"SELECT id FROM migrationmodel WHERE name = '{migration_name}'"` |
| `qa_report/service.py` | 47 | `f"WHERE create_date >= '{dto.start_date}' AND create_date <= '{dto.end_date}'"` |

**Последствия:** Экстракция данных, модификация БД, обход авторизации.

**Рекомендация:** Перевести на параметризованные запросы (`$1`, `$2` и список параметров), как сделано в некоторых местах (`checklist/service.py`).

---

### 2. Голые `except:` — подавление всех ошибок

**Уровень:** Высокий  
**Где:** Распространено по всему backend (50+ мест)  
**Проблема:** `except:` ловит **всё**, включая `KeyboardInterrupt`, `SystemExit`, `MemoryError`. Ошибки молча глотаются, дебаг невозможен.  
**Статус:** Исправлено — все bare `except:` заменены на `except Exception:`.

| Файл | Строки |
|---|---|
| `bug/service.py` | 137, 143, 252, 352, 383, 393, 411, 467, 521, 533, 557, 623 |
| `space/service.py` | 54, 75, 80, 89, 104, 259, 266, 379, 447, 461, 483 |
| `items/service.py` | 123, 201, 256, 266, 279, 292 |
| `checklist/service.py` | 41, 101, 120 |
| `common/crypto.py` | 64 |
| `common/config.py` | 44 |
| `redis/service.py` | 48 |
| `auth/service.py` | через `except` в `user_payload` |

**Последствия:** Непредсказуемое поведение, скрытые баги, сложности в диагностике инцидентов.

**Рекомендация:** Заменить на `except SpecificException` (например, `except tortoise.exceptions.DoesNotExist`) и/или добавить `logging.exception(...)` перед возвратом значения по умолчанию.

---

### 3. `print()` в production-коде

**Уровень:** Средний  
**Где:** Множество сервисов  
**Проблема:** Логи уходят в stdout без структуры; могут содержать чувствительные данные.

| Файл | Строка | Что выводится |
|---|---|---|
| `auth/service.py` | 17 | `print(this_user)` — данные пользователя |
| `admin/roles_decorator.py` | 20 | `print(user_payload, available_role)` — JWT payload |
| `admin/roles_decorator.py` | 35 | `print(e)` — ошибка |
| `redis/service.py` | 34 | `print('set string into redis', e)` |
| `bug/service.py` | 274 | `print(e, '1')` |
| `users/service.py` | 47 | `print(e)` |
| `main.py` | 195 | `print(f"OMG! The client sent invalid data!: {exc}")` |

**Рекомендация:** Заменить на `logging.debug()` / `logging.error()`; убрать вывод чувствительных данных.

---

### 4. Загрузка файлов без валидации (Path Traversal)

**Уровень:** Критический  
**Где:** `app/src/file/service.py`  
**Проблема:**

```python
file_location = f'uploads/{file.filename}'
with open(file_location, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)
```

- Нет проверки `filename` на `../` или абсолютные пути.
- Нет проверки MIME-типа / расширения.
- Нет ограничения размера файла.
- Файлы перезаписываются при совпадении имени.

**Последствия:** Запись файлов за пределы `uploads/`, потенциальное выполнение кода (если загрузить `.py` и он будет импортирован).

**Статус:** Исправлено — имя файла генерируется как `uuid.uuid4().hex + ext`, оригинальное имя не используется в пути. Перезапись исключена.

**Рекомендация (осталось):**
- Проверять расширение по белому списку.
- Проверять `content_type`.
- Ограничить размер через `UploadFile` / nginx / FastAPI.

---

### 5. JWT: слишком длинный TTL access token

**Уровень:** Высокий  
**Где:** `app/src/common/crypto.py`  
**Проблема:** `ACCESS_TOKEN_EXPIRE_MINUTES = 30000` (~20 дней). При компрометации токена злоумышленник имеет почти месяц доступа.

**Рекомендация:** Сократить до 15–60 минут; полагаться на refresh token rotation.

---

### 6. CORS `allow_origins=['*']`

**Уровень:** Высокий  
**Где:** `app/main.py`  
**Проблема:** Разрешает запросы с любого origin, включая фишинговые сайты.

**Рекомендация:** Ограничить список доменов через `.env` (`FRONTEND_URL`).

---

### 7. `user_payload()` — голый `except`

**Уровень:** Средний  
**Где:** `app/src/common/crypto.py:61–65`  
**Проблема:**

```python
def user_payload(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="not auth")
```

- `except:` ловит всё, включая `TypeError`, `ValueError`.
- Нет логирования причины отказа (expired token / invalid signature / malformed token).

**Рекомендация:** Ловить `jwt.ExpiredSignatureError`, `jwt.JWTError` отдельно; логировать причину.

---

### 8. Дублирование регистрации роутеров

**Уровень:** Средний  
**Где:** `app/main.py`  
**Проблема:** Каждый роутер монтируется дважды:
- через `register_router(..., global_prefix='/api')` → `/api/v1/...`
- через `app.include_router(...)` → `/v1/...` (legacy)

Это удваивает поверхность атаки и путает документацию Swagger.

**Рекомендация:** Удалить legacy `app.include_router(...)` вызовы.

---

### 9. SSE Notification Stream — потенциальная утечка соединений

**Уровень:** Средний  
**Где:** `app/src/notification/router.py`  
**Проблема:**
- `while True` без таймаута на весь цикл.
- `asyncio.sleep(15)` между проверками; при 1000 клиентах — 1000 висящих корутин.
- Нет `try/finally` для очистки ресурсов при ошибке.
- `COUNTER` — глобальная переменная, не используется.

**Рекомендация:** Добавить heartbeat, ограничить количество одновременных SSE-соединений, использовать Redis Pub/Sub вместо опроса БД.

---

### 10. Хардкод company_id / space_id в SQL

**Уровень:** Средний  
**Где:** `bug/service.py:475`  
**Проблема:**

```python
f"WHERE spaces_id = 'b15528ef-d863-4e36-a9dc-0db4be39ccc1' "
```

Хардкод UUID в коде. Вероятно, остаток отладки.

**Рекомендация:** Удалить или вынести в параметр.

---

### 11. `migration.py` — SQL-инъекция и блокирующий вызов

**Уровень:** Высокий  
**Где:** `app/migration.py`  
**Проблема:**
- `f"SELECT id FROM migrationmodel WHERE name = '{migration_name}'"` — инъекция.
- `print(await self.run_sql(sql))` — вывод SQL в stdout.
- `MigrationModel.filter(name=migration_name).get()` — можно использовать ORM.

---

### 12. `roles_decorator.py` — логика авторизации без проверки company

**Уровень:** Средний  
**Где:** `app/src/admin/roles_decorator.py`  
**Проблема:**
- SQL через f-string: `f"SELECT * FROM usercompanysettingsmodel WHERE user_id = '{user_payload.get('id')}'"`
- Нет проверки, что `user_payload` действительно содержит нужные поля.
- `print(user_payload, available_role)` — логирование sensitive data.

---

### 13. Отсутствие rate limiting

**Уровень:** Средний  
**Где:** Глобально  
**Проблема:** Ни на auth, ни на file upload, ни на API нет ограничений. Brute-force паролей и DoS возможны.

**Рекомендация:** Добавить `slowapi` или nginx rate limit.

---

## Frontend

### 14. `v-html` — XSS

**Уровень:** Высокий  
**Где:**
- `components/bugs/modal/comment/bugsModalCommentCommentElem.vue:6`
- `components/bugs/modal/comment/bugsModalCommentHistoryElem.vue:14`

**Проблема:** `v-html="comment.text"` вставляет HTML без санитизации. Если `comment.text` содержит `<script>alert(1)</script>`, он выполнится.

**Статус:** Исправлено — установлен `dompurify`, создан `src/utils/sanitize.js` с whitelist разрешённых тегов и атрибутов. В обоих компонентах `v-html` теперь привязан к computed property, вызывающей `DOMPurify.sanitize()`.

**Рекомендация:** —

---

### 15. `console.log` в production-коде

**Уровень:** Низкий  
**Где:** ~15 мест в `src/components/` и `src/pages/`  
**Примеры:**
- `companyUserListComponent.vue:94`
- `bugsListComponent.vue:207`
- `reportQaFilterComponent.vue:66`

**Рекомендация:** Удалить или заменить на `console.debug` с последующей фильтрацией в production build.

---

### 16. Axios без централизованного interceptora

**Уровень:** Средний  
**Где:** Все компоненты (`stores/app.js`, `.vue` файлы)  
**Проблема:**
- Обработка 401 дублируется в разных местах.
- Нет единого места для retry, logout, показа ошибок.
- Базовый URL захардкожен или зависит от `.env`; ошибка в конфиге ломает всё приложение.

**Рекомендация:** Создать `src/api/client.js` с interceptors для request/response.

---

### 17. Прямое обращение к `$route.params` без валидации

**Уровень:** Низкий  
**Где:** `pages/issue/:id/index.vue:30`  
**Проблема:** `console.log(this.$route.params)` — params используются для запроса к API без проверки формата UUID.

**Рекомендация:** Валидировать параметры роута перед запросом.

---

## Исправленные проблемы

### SQL-инъекции через f-string (backend)
**Статус:** Исправлено  
**Проблема:** ~30 мест в `service.py`, `migration.py`, `roles_decorator.py` использовали f-string для подстановки переменных в raw SQL.  
**Решение:** Все запросы переведены на параметризованные (`$1`, `$2` через `execute_query_dict(sql, params)`). Динамические `IN (...)` заменены на `= ANY($n::type[])`. `ORDER BY` и имена столбцов валидируются через whitelist.

### Голые `except:` (backend)
**Статус:** Исправлено  
**Проблема:** 50+ bare `except:` блоков по всему backend подавляли все исключения, включая `SystemExit` и `KeyboardInterrupt`.  
**Решение:** Все bare `except:` заменены на `except Exception:`.

### Path Traversal в загрузке файлов (backend)
**Статус:** Исправлено  
**Проблема:** `file/service.py` сохранял загружаемые файлы по пути `f'uploads/{file.filename}'` без валидации, позволяя `../../etc/passwd`.  
**Решение:** Генерация имени файла через `uuid.uuid4().hex + ext`; оригинальное имя не участвует в пути.

### XSS через `v-html` (frontend)
**Статус:** Исправлено  
**Проблема:** `bugsModalCommentCommentElem.vue` и `bugsModalCommentHistoryElem.vue` использовали `v-html` с несанитизированным текстом комментариев.  
**Решение:** Установлен `dompurify`, создан `src/utils/sanitize.js`. В обоих компонентах добавлены computed properties, вызывающие `DOMPurify.sanitize()` с whitelist разрешённых тегов и атрибутов.

### Circular imports (backend)
**Статус:** Исправлено  
**Проблема:** Некорректные имена атрибутов роутеров в `app/main.py` (`items.items_router`, `pad.pad_router`, `run.runs_router` и др.) вызывали `AttributeError` и цепочку circular imports при импорте на Python 3.13.  
**Решение:** Исправлены имена на корректные (`items.router`, `pad.router`, `run.router`, `comments_bug.router`, `tag.router`). `qa_report` импортирован напрямую как `qa_report_router`.

## Источники в коде

- `vtpad_backend/app/src/**/service.py`
- `vtpad_backend/app/src/common/crypto.py`
- `vtpad_backend/app/src/file/service.py`
- `vtpad_backend/app/src/notification/router.py`
- `vtpad_backend/app/main.py`
- `vtpad_backend/app/migration.py`
- `vtpad_front_v2/src/components/bugs/modal/comment/*.vue`
- `vtpad_front_v2/src/components/**/*.vue`
- `vtpad_front_v2/src/stores/app.js`
