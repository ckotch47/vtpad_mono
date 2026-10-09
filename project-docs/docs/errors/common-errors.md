# Ошибки и ограничения (baseline)

## Что описывает

Известные ограничения и типичные ошибки в текущей кодовой базе.

## Известные ограничения

1. **Нет тестов** — ни unit, ни integration, ни e2e. Регрессии не отслеживаются автоматически.
2. **Raw SQL в сервисах** — при рефакторинге моделей запросы ломаются молча.
3. **CORS `allow_origins=['*']`** — открыт для любого origin.
4. **Нет rate limiting** — уязвим для brute-force.
5. **Access token TTL ~30000 мин** — фактически long-lived token.
6. **Нет формального migration framework** — schema изменяется JSON-миграциями при старте. Обычные миграции транзакционны и попадают в ledger после успешного DDL; online-index миграции выполняются вне транзакции, перед retry удаляют только свои invalid indexes и записываются в ledger лишь после полного успеха.
7. **Два монтирования роутеров** — `/api/v1/...` и `/v1/...` (legacy), что может путать.
8. **Нет выделенного API-клиента на фронтенде** — Axios дублируется в компонентах.
9. **Нет уникального ограничения membership** — прикладная проверка предотвращает обычный повторный запрос добавления участника, но параллельные запросы всё ещё могут создать дубликат. Для полного устранения потребуется отдельная migration с уникальным индексом `(userId, spaceId)`.
10. **Старые run без timer intervals** — календарные даты могут быть доступны, но активное время и паузы неизвестны; UI/API должны показывать отсутствие замера, а не `0`.

Подробный разбор потенциально опасных функций и паттернов — в разделе [Слабые места в коде](code-weaknesses.md).

## Типичные ошибки

| Ошибка | Причина | Где искать |
|---|---|---|
| `500` на фильтрации bugs | Raw SQL с hardcoded column name | `app/src/bug/service.py` |
| В модалке бага не переключается вкладка History | Разный тип `value` у `v-tab` и `v-tabs-window-item` (`number` vs `string`) | `vtpad_front_v2/src/components/bugs/modal/bugsModalHistoryComponentV2.vue` |
| Комментарий в модалке бага не сохраняется | Отсутствует `bug.id` или отправляется пустой HTML (`<p></p>`) | `vtpad_front_v2/src/components/bugs/modal/bugsModalCommentComponent.vue` |
| `403` или лог-ошибка в уведомлениях при отсутствии assigner | Background task пытался создать notification с пустым `assigner_id` | `vtpad_backend/app/src/bug/service.py`, `vtpad_backend/app/src/comments/service.py` |
| `401` после долгого простоя | Access token expired, refresh failed | `app/src/auth/service.py`, Redis |
| `403` при чтении списка suites | REST и MCP проверяют membership/роль в запрошенном space до поиска; клиенту нужно выбрать доступный space | `app/src/test_suite/router.py`, `app/src/mcp/tools/test_suites.py` |
| `404` при чтении/записи custom field | Definition или entity отсутствует либо находится в другом space; чужие UUID не раскрываются | `app/src/custom_field/service.py` |
| `422` при сохранении custom field | Тип/вариант значения не совпадает с definition, select/multiselect не имеет уникальных вариантов, отсутствует required value, либо изменение type/options сделало live values несовместимыми | `app/src/custom_field/service.py`, `app/src/test_case/service.py` |
| Пустой экран после открытия `/` или входа | Главная страница и успешная авторизация переходили на `/space` без `spaceId`; существует только маршрут `/space/:spaceId` | `vtpad_front_v2/src/pages/index.vue`, `vtpad_front_v2/src/components/auth/authComponent.vue` |

## Исправленные дефекты

1. `PUT /api/v1/comment/{comment_id}` теперь возвращает `404`, если комментарий не найден, вместо `500`.
2. `POST /api/v1/comment/{bug_id}` теперь возвращает `404`, если bug не существует, до создания комментария.
3. `PATCH /api/v2/bugs/{bug_id}` и `PUT /api/v1/bugs/{bug_id}` теперь сначала проверяют существование бага и возвращают `404`, если id не найден.
4. Обновление бага теперь допускает пустые строковые значения для редактируемых полей и корректно обрабатывает `tags=[]` как очистку тегов.
5. Background tasks для уведомлений теперь пропускают пустой `assigner_id`/`create_user_id` и не падают на UUID conversion.
6. Bugs list filtering now respects `show_closed`; when enabled, `HOLD` and `CLOSED` are no longer excluded by default.
7. MCP `hard_delete_suite` now imports cascade helpers correctly and no longer fails with `name '_delete_case_cascade' is not defined`.
8. В деталях test run круглый индикатор результата циклично меняет статус без повторной загрузки страницы; чекбоксы видны у всех результатов и в active run позволяют массово назначить любой статус, включая `not_run`. Любой результат active run можно исправить через диалог. Изменение комментария или длительности не меняет исполнителя и время выполнения; отдельная ссылка открывает полный testcase в новой вкладке, не меняя текущий просмотр run.
9. Tech Docs безопасно отображает длинный `Source URL` в одну строку с подсказкой полного значения, не давая ему обрезать описание: секция ссылки не растягивает flex-карточку, а тело документа прокручивается. Редактор создаёт rich-text ссылки через структурированный TipTap content, а не через интерполяцию HTML.
10. V2 test run больше не создаётся по неявному "всем кейсам space": preview и create требуют ровно один явный непустой источник.
11. Удаление testcase с историей выполнения переводит его в `deprecated`, сохраняя результаты и snapshots уже созданных runs.
12. Списки test cases, test suites, test plans и test runs показывают имя создателя; у исторических записей без автора отображается `—`.
13. Повторное добавление уже существующего участника в space возвращает актуальный список участников, а не `null`; проверка владельца больше не даёт `500`, если у пользователя нет строки membership, и корректно допускает только owner либо активного `company_admin` той же company. Добавить можно только активного пользователя этой company.
14. Очистка поиска кейсов в деталях suite может передавать `null`; фильтр нормализует его в пустую строку, ищет title/short name в выбранной секции, различает пустую секцию, отсутствие совпадений и ошибку загрузки, а для ошибки предоставляет повторный запрос.
15. Сортировка секций suite доступна через REST и MCP `sort_sections`; оба пути требуют ровно один `sort_before_id` или `sort_after_id`, проверяют одинаковые `suite_id` и `parent_id` плюс membership в space, затем транзакционно переписывают порядок siblings. UI при сетевой ошибке возвращает исходный порядок и показывает Retry.
16. Если short name bug неоднозначен в пространстве run, REST и MCP возвращают `409`; если такого bug в space нет — `404`. Изменять связи и legacy references можно только в active run; в другом состоянии запрос возвращает `409`. MCP `link_bug_to_result` и `unlink_bug_from_result` теперь также требуют active run и однозначный short name. Quick-create retry должен отправлять прежние `operation_id` и тело; повторное использование ID с другим actor/result/body возвращает `409`.
17. Если исходный bug quick-create удалён, повтор того же `operation_id` возвращает `410`; квитанция сохраняется, чтобы повтор запроса не создал новый bug.
18. Run detail должен нормализовать UUID id перед чтением timer summary; иначе вызов сервиса с `UUID`-объектом вместо строки возвращал `404`, хотя run существует.
19. Tech Docs REST unlink больше не меняет повреждённую cross-space связь: роут проверяет доступ к документу и testcase, а сервис повторно сверяет same-space пару. Повреждённый legacy `parent_id` больше не раскрывается в REST/MCP ответах и отображается как корневой документ без родителя.
20. После закрытия левой панели пространств переключатель остаётся поверх содержимого и сохраняет возможность открыть панель без обновления страницы.
21. Tech Docs различает пустое дерево, загрузку и ошибку: `Create first page` появляется только после успешно загруженного пустого списка; при ошибке доступен Retry.
22. Case full-text search должен возвращать совпадения по title/description даже у записей без `short_name`; отсутствие идентификатора не должно блокировать результат после подсчёта совпадений.
22. Главная страница, успешный вход и возврат после удаления space переходят на существующий `/company/spaces` через Vue Router; пустая заглушка `/space` больше не является точкой входа.

## Источники в коде

- `vtpad_backend/app/main.py`
- `vtpad_backend/app/src/bug/service.py`
- `vtpad_backend/app/src/common/config.py`
- `vtpad_front_v2/src/stores/app.js`
- `vtpad_front_v2/src/components/test-suites/detail/SuiteCasesPanel.vue`
- `vtpad_front_v2/src/composables/useTestSuiteDetail.js`
