# Карта сервисов и endpoint'ов

## Что описывает

Эта страница фиксирует baseline endpoint'ов по текущему коду backend.

Здесь указаны маршруты, которые явно видны в коде роутеров.

## Preconditions

- Доступен исходный код `vtpad_backend`.
- Backend монтирует роутеры дважды: через `register_router(..., global_prefix='/api')` и через `app.include_router(...)`.
  - Первый вариант добавляет `/api` к префиксу роутера.
  - Второй вариант — legacy, без `/api`.
- Далее указаны пути с префиксом `/api` как основные.

## Общие правила baseline

- Большинство endpoints защищены `Depends(bearer)` (JWT access token).
- Некоторые endpoints дополнительно требуют `Depends(check_user_into_space)` для авторизации на уровне space.
- Auth endpoints (`/api/v1/auth`) — публичные.

## `vtpad_backend` — Core API

### Auth

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/auth` | Public | login; возвращает access + refresh tokens |
| POST | `/api/v1/auth/refresh` | Public | refresh token -> новая пара tokens |

### Users

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/user` | Public (deprecated) | регистрация |
| GET | `/api/v1/user` | JWT | текущий пользователь |
| PATCH | `/api/v1/user` | JWT | обновление профиля |
| GET | `/api/v1/user/search/by-mail` | JWT | поиск пользователей по email |

### Spaces

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/space` | JWT | список spaces |
| POST | `/api/v1/space` | JWT | создание space |
| GET | `/api/v1/space/{space_id}` | JWT + space check | детали space |
| GET | `/api/v1/space/{space_id}/users` | JWT + space check | пользователи space |
| PUT | `/api/v1/space/{space_id}` | JWT + space check | обновление space |
| PUT | `/api/v1/space/{space_id}/user` | JWT + space check + owner / active company admin | добавление активного пользователя той же company; повторный запрос возвращает актуальный список участников |
| DELETE | `/api/v1/space/{space_id}/user/{user_id}` | JWT + space check | удаление пользователя |
| PATCH | `/api/v1/space/{space_id}/user/{user_id}` | JWT + space check | обновление прав пользователя |
| PUT | `/api/v1/space/{space_id}/user-make-owner/{user_id}` | JWT + space check | назначение владельца |
| DELETE | `/api/v1/space/{space_id}` | JWT + space check | удаление space |
| GET | `/api/v1/space/{space_id}/all_runs` | JWT + space check | все runs space |
| GET | `/api/v1/space/{space_id}/statistic` | JWT + space check | статистика space |
| GET | `/api/v1/space/by-short/{short_name}` | JWT | получение по short name |

### Pads

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/pad/{space_id}` | JWT + space check | список pads |
| GET | `/api/v1/pad/detail/{pad_id}` | JWT | детали pad |
| POST | `/api/v1/pad/{space_id}` | JWT + space check | создание pad |
| PATCH | `/api/v1/pad/{pad_id}` | JWT | обновление pad |
| DELETE | `/api/v1/pad/{pad_id}` | JWT | удаление pad |
| PATCH | `/api/v1/pad/sort/{pad_id}` | JWT | сортировка |

### Pad Folders

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/pad-folder/{space_id}` | JWT + space check | список folders |
| GET | `/api/v1/pad-folder/detail/{folder_id}` | JWT | детали folder |
| POST | `/api/v1/pad-folder/{space_id}` | JWT + space check | создание folder |
| PATCH | `/api/v1/pad-folder/{folder_id}` | JWT | обновление folder |
| DELETE | `/api/v1/pad-folder/{folder_id}` | JWT | удаление folder |

### Runs

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/runs/{pad_id}` | JWT | создание run |
| DELETE | `/api/v1/runs/{run_id}` | JWT | удаление run |
| GET | `/api/v1/runs/items/{run_id}` | JWT | items run |
| GET | `/api/v1/runs/{run_id}` | JWT | детали run |
| GET | `/api/v1/runs/all/{pad_id}` | JWT | все runs pad |
| GET | `/api/v1/runs/filter/{space_id}` | JWT + space check | фильтры |
| GET | `/api/v1/runs/by-filter/{space_id}` | JWT + space check | runs с фильтром |
| PATCH | `/api/v1/runs/{run_id}` | JWT | обновление run |

### Run Items

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| PATCH | `/api/v1/runitems/{item_id}` | JWT | обновление статуса item |

### V2 Test Management

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v2/test-run/preview` | JWT + space check | валидирует ровно один источник run и возвращает состав с suite, root→leaf `section_path` и `source_hash`; путь учитывается при проверке устаревшего preview |
| POST | `/api/v2/test-run` | JWT + space check | создаёт run и snapshots результатов для cases любого статуса; устаревший preview возвращает `409` |
| GET | `/api/v2/test-run/space/{space_id}` | JWT + space check | список, поддерживает `search`, `milestone_id`, `environment_id`; возвращает nullable `created_by` с `{id, username}` |
| GET | `/api/v2/test-run/{run_id}` | JWT + space check | метаданные run |
| GET | `/api/v2/test-run/{run_id}/detail` | JWT + space check | результаты со suite и `section_path` (root→leaf), snapshot/legacy-признак, run timer и сумма фактических длительностей; `linked_bug_ids` остаётся массивом, `linked_bug_ids_raw` содержит неизменённое legacy JSON (включая `null`), `linked_bugs` содержит новые UUID-связи |
| PATCH | `/api/v2/test-run/{run_id}` | JWT + space check | обновляет метаданные; статус передаётся отдельным lifecycle endpoint |
| POST | `/api/v2/test-run/{run_id}/start` | JWT + space check | переводит run из `draft` в `active` и открывает общий timer interval |
| POST | `/api/v2/test-run/{run_id}/pause` | JWT + space check | закрывает текущий общий timer interval |
| POST | `/api/v2/test-run/{run_id}/resume` | JWT + space check | открывает следующий общий timer interval |
| POST | `/api/v2/test-run/{run_id}/complete` | JWT + space check | завершает active run и закрывает открытый timer interval |
| PATCH | `/api/v2/test-run/result/{result_id}` | JWT + space check | меняет статус и детали результата только в active run; фактическая длительность `>= 0`, `NULL` означает «нет замера»; ответ включает массив `linked_bug_ids` и оригинал `linked_bug_ids_raw` |
| POST | `/api/v2/test-run/result/{result_id}/bugs/{bug_uuid}` | JWT + space check | идемпотентно связывает result с bug по `link_uuid` в том же space |
| DELETE | `/api/v2/test-run/result/{result_id}/bugs/{bug_uuid}` | JWT + space check | удаляет UUID-связь с bug в том же space |
| POST | `/api/v2/test-run/result/{result_id}/bugs/link` | JWT + space check | short-name convenience wrapper для UUID-связи; только для active run и ровно одного совпадения, неоднозначность возвращает `409` |
| DELETE | `/api/v2/test-run/result/{result_id}/bugs/link` | JWT + space check | short-name convenience wrapper с теми же active-run и ambiguity проверками |
| POST | `/api/v2/test-run/result/{result_id}/bugs` | JWT + space check | атомарно создаёт bug и UUID-связь; повторяет результат по `operation_id` при совпадении actor/result/body |
| PATCH | `/api/v2/test-run/result/bulk` | JWT + space check | массово меняет статус результатов одного active run; поддерживает возврат в `not_run` |
| PATCH | `/api/v2/test-case/{testcase_id}` | JWT + space check | обновляет только явно переданные поля, включая оценку `estimated_duration_seconds >= 0`; явный `section_id: null` снимает кейс с секции и оставляет его в указанном (или текущем) suite — UI показывает его в виртуальной секции `Default`; `null` остальных полей игнорируется. |
| POST | `/api/v2/test-case/{testcase_id}/move` | JWT + space check | явно перемещает кейс в тело `{suite_id, section_id}`; оба поля обязательны, `section_id: null` означает виртуальную секцию `Default` указанного suite. Suite и section проверяются в space кейса; чужая/несуществующая ссылка возвращает общий `404`, section другого suite в том же space — `422`. Ответ содержит `id`, `space_id`, `suite_id`, `section_id`; перемещение не создаёт content version. |
| GET | `/api/v2/test-case/{testcase_id}/versions` | JWT + space check | история версий testcase |
| GET | `/api/v2/test-case/{testcase_id}/versions/{version_id}` | JWT + space check | конкретная версия testcase |
| GET | `/api/v2/test-case/{testcase_id}/versions/diff` | JWT + space check | сравнение двух версий |
| POST | `/api/v2/test-case/{testcase_id}/versions/{version_id}/restore` | JWT + space check | создаёт новую текущую версию из выбранной |
| GET | `/api/v2/test-case/{testcase_id}/runs` | JWT + space check | история результата кейса с фактическим временем и доступными timing полями связанного run |
| GET/PUT | `/api/v2/test-case/{testcase_id}/tech-docs` | JWT + space check | получает/заменяет связи testcase с Tech Docs |
| GET/PUT | `/api/v2/tech-doc/{tech_doc_id}/test-cases` | JWT + space check | получает/заменяет связи Tech Doc с test cases |
| POST | `/api/v2/traceability/tech-doc/{tech_doc_id}/test-case/{testcase_id}` | JWT + space check | создаёт same-space связь Tech Doc и testcase |
| DELETE | `/api/v2/traceability/tech-doc/{tech_doc_id}/test-case/{testcase_id}` | JWT + access to both spaces | удаляет связь только для same-space пары; service повторяет проверку |

### V2 Sections

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/section/suite/{suite_id}` | JWT | секции suite |
| GET | `/api/v2/section/suite/{suite_id}/tree` | JWT | дерево секций suite |
| POST | `/api/v2/section/` | JWT | создание секции |
| PATCH | `/api/v2/section/{section_id}` | JWT | обновление секции |
| DELETE | `/api/v2/section/{section_id}` | JWT | удаление секции |
| PATCH | `/api/v2/section/sort/{section_id}` | JWT + suite space check | body задаёт ровно один `sort_before_id` или `sort_after_id`; neighbor должен быть sibling в той же suite и parent. Возвращает упорядоченный список siblings. Неверный body — 422; self/non-sibling — 422; неучастник space — 403. Порядок записывается атомарно. MCP counterpart: `sort_sections` с теми же проверками. |
| GET | `/api/v2/tech-doc/space/{space_id}` | JWT + space check | список Tech Docs в space |
| GET | `/api/v2/tech-doc/space/{space_id}/tree` | JWT + space check | дерево Tech Docs в space |
| GET | `/api/v2/tech-doc/{doc_id}` | JWT + space check | получает документ после проверки доступа к его space |
| POST | `/api/v2/tech-doc/` | JWT + space check | создаёт документ; родитель должен быть в том же space |
| PATCH | `/api/v2/tech-doc/{doc_id}` | JWT + space check | обновляет документ; родитель должен быть в том же space, переносы сериализуются по space и не создают циклы |
| DELETE | `/api/v2/tech-doc/{doc_id}` | JWT + space check | удаляет документ после проверки доступа к его space |

Списки V2 test cases, test suites и test plans также возвращают nullable `created_by` с `{id, username}`. Почта и другие персональные данные автора не включаются.

### Items (Pad Items)

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/items/{pad_id}` | JWT | список items |
| POST | `/api/v1/items/{pad_id}` | JWT | создание item |
| PUT | `/api/v1/items/{item_id}` | JWT | обновление item |
| DELETE | `/api/v1/items/{item_id}` | JWT | удаление item |
| PATCH | `/api/v1/items/{item_id}` | JWT | обновление sort/порядка |

### Bugs

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/bugs` | JWT | создание bug |
| GET | `/api/v1/bugs` | JWT | список bugs (с фильтрами) |
| GET | `/api/v1/bugs/detail/{bug_id}` | JWT | детали bug |
| GET | `/api/v1/bugs/detail-short` | JWT | детали по short name |
| GET | `/api/v1/bugs/id/by-short` | JWT (deprecated) | bug id по short name |
| PUT | `/api/v1/bugs/{bug_id}` | JWT (deprecated) | обновление bug |
| GET | `/api/v1/bugs/filters` | JWT | доступные фильтры |
| PUT | `/api/v1/bugs/{bug_id}/tag` | JWT | добавление tag к bug |
| DELETE | `/api/v1/bugs/{bug_id}/tag/{tag_id}` | JWT | удаление tag из bug |
| GET | `/api/v1/bugs/state-enum` | JWT | enum статусов |
| GET | `/api/v2/bugs/space/{space_id}/by-link/{link_uuid}` | JWT + space membership | детали bug по стабильному UUID связи; выборка проверяет `bugsmodel.spaces_id` |

### Analytics — linked defects

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/analytics/space/{space_id}/bugs` | JWT + space membership | summary уникальных bugs/связей и страница bug; фильтры `status`, `run_id`, `suite_id`; для каждого bug возвращается максимум 25 пар `result_links`, `result_links_truncated` сообщает об усечении; `link_count` содержит полный счётчик |
| GET | `/api/v2/analytics/space/{space_id}/bugs/by-run` | JWT + space membership | пагинированные уникальные bugs и связи по run |
| GET | `/api/v2/analytics/space/{space_id}/bugs/by-suite` | JWT + space membership | пагинированные уникальные bugs и связи по suite snapshot; legacy/неизвестная suite имеет явную атрибуцию |

Аналитика читает только `test_result_bug_link` и сопоставляет bug и run в одном space; legacy JSON `linked_bug_ids` в метрики не входит. Статусы сводятся к `OPEN`, `FIXED`, `REOPEN`, `OTHER`.

Параметры фильтра для `GET /api/v1/bugs` включают `q` (поиск по `title` и `short_name`), а также существующие фильтры (`state`, `assigner_id`, `create_user`, `tag`, `external_link`, `create_date*`, `estimate_date*`, `order_*`, `skip`, `limit`).

### Bug Comments

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/comment/{bug_id}` | JWT | список comments |
| POST | `/api/v1/comment/{bug_id}` | JWT | создание comment |
| PUT | `/api/v1/comment/{comment_id}` | JWT | обновление comment |
| DELETE | `/api/v1/comment/{comment_id}` | JWT | удаление comment |

### Tags

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/tag/{space_id}` | JWT + space check | список tags |
| PUT | `/api/v1/tag/{tag_id}` | JWT | обновление tag |
| POST | `/api/v1/tag/{space_id}` | JWT + space check | создание tag |
| DELETE | `/api/v1/tag/{tag_id}` | JWT | удаление tag |

### Testcases

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/testcases/filter/{space_id}` | JWT + space check | фильтрованный список |
| GET | `/api/v1/testcases/{space_id}` | JWT + space check | список (с сортировкой) |
| GET | `/api/v1/testcases/paditem/{paditem_id}` | JWT (deprecated) | по pad item |
| GET | `/api/v1/testcases/detail/{testcase_id}` | JWT | детали |
| GET | `/api/v1/testcases/item/{item_id}` | JWT | по item |
| POST | `/api/v1/testcases` | JWT | создание |
| PATCH | `/api/v1/testcases/{testcase_id}` | JWT | обновление |
| POST | `/api/v1/testcases/image/{testcase_id}` | JWT (deprecated) | загрузка image |
| DELETE | `/api/v1/testcases/image/{testcase_id}/{image_id}` | JWT (deprecated) | удаление image |
| DELETE | `/api/v1/testcases/{testcase_id}` | JWT | удаление |
| GET | `/api/v1/testcases/shortname/{short_name}` | JWT | по short name |

### Testcases RunItem / PadItem

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| PUT | `/api/v1/testcases-paditem/{item_id}/{testcase_id}` | JWT (deprecated) | привязка |
| DELETE | `/api/v1/testcases-paditem/{item_id}/{testcase_id}` | JWT (deprecated) | отвязка |
| PATCH | `/api/v1/testcases-runitem/{element_id}` | JWT | обновление связи run-item -> testcase |

### Checklists

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/checklist/list/{space_id}` | JWT + space check | список |
| GET | `/api/v1/checklist/{checklist_id}` | JWT | детали |
| POST | `/api/v1/checklist/{space_id}` | JWT + space check | создание |
| PATCH | `/api/v1/checklist/{checklist_id}` | JWT | обновление |
| DELETE | `/api/v1/checklist/{checklist_id}` | JWT | удаление |
| GET | `/api/v1/checklist/by-short/{short_name}` | JWT | по short name |

### Files / Uploads

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| POST | `/api/v1/file` | JWT | upload avatar |
| POST | `/api/v1/file/image` | JWT | upload image |
| GET | `/api/v1/file/{file_id}` | Public | скачивание файла |

### Notifications

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/notification/stream` | JWT | SSE stream уведомлений |
| GET | `/api/v1/notification/unread-count` | JWT | количество непрочитанных |
| GET | `/api/v1/notification` | JWT | список уведомлений |
| PUT | `/api/v1/notification/{notification_id}/read` | JWT | прочитать одно |
| PUT | `/api/v1/notification/read-all` | JWT | прочитать все |

### News

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/news` | JWT | список news |
| PATCH | `/api/v1/news/read` | JWT | отметить прочитанным |
| GET | `/api/v1/news/unread` | JWT | непрочитанные |

### Reports

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/report/test/list/{space_id}` | JWT + space check | список тестов для отчёта |
| GET | `/api/v1/report/test/detail/{test_id}` | JWT | детали теста для отчёта |

### QA Report

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/qa-report/users` | JWT | пользователи для QA отчёта |
| GET | `/api/qa-report/bug-list` | JWT | список багов для QA отчёта |

### Notes

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v1/notes/{space_id}` | JWT + space check | список notes |
| POST | `/api/v1/notes/{space_id}` | JWT + space check | создание note |
| PATCH | `/api/v1/notes/{note_id}` | — | обновление note |
| DELETE | `/api/v1/notes/{note_id}` | — | удаление note |

### Admin — Company

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/amin/company/list` | JWT | список компаний |
| POST | `/api/v2/amin/company` | JWT | создание компании |
| PUT | `/api/v2/amin/company/{company_id}` | JWT | обновление компании |
| GET | `/api/v2/amin/company/detail/{company_id}` | — | детали компании |

### Admin — Company User Settings

| Method | Path | Auth/Access | Примечания |
| --- | --- | --- | --- |
| GET | `/api/v2/company-user/list` | JWT | список пользователей |
| PUT | `/api/v2/company-user/{user_id}` | JWT | обновление пользователя |
| POST | `/api/v2/company-user` | JWT | создание пользователя |
| PUT | `/api/v2/company-user/{user_id}/reset-password` | JWT | сброс пароля |
| DELETE | `/api/v2/company-user/{user_id}` | JWT (hidden) | удаление |

## Legacy non-prefixed routes

В `app/main.py` роутеры дополнительно монтируются через `app.include_router(...)` без `/api`.
Это означает, что все пути выше доступны и без `/api` (например, `/v1/space` вместо `/api/v1/space`).

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/src/**/router.py`
