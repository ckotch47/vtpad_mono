# VTPad Roadmap

## 🚀 Core (Done)
- [x] Test Suite / Section / Test Case / Test Run / Test Result модели
- [x] Server-side pagination, sorting, search для Cases, Suites, Runs
- [x] URL query params sync (page, search, sort, filters)
- [x] Bulk actions: delete + change status для Cases
- [x] Tiptap editor для description, preconditions, steps, expected_results
- [x] Test Case versioning (version snapshots)
- [x] Linked bugs для Test Results
- [x] Test Run results grouped by section
- [x] Stats cards в Suite Detail (total, manual, checklist, automated)
- [x] Section tree с context menu (add sub-section, rename, delete)
- [x] Add existing test cases to section
- [x] Test Case view modal из Suite Detail

---

## 🤖 AI Integration

### MCP Server (FastAPI)
- [ ] **MCP Server** — встроенный в FastAPI или отдельный сервис
  - `search_cases(query: str)` — семантический поиск по test cases
  - `find_similar_cases(case_id: str)` — найти похожие кейсы
  - `create_case(suite_id, section_id, title, steps, ...)` — создание кейса
  - `update_case(id, ...)` — редактирование
  - `get_suite_tree(suite_id)` — структура suite + sections
  - `create_run(suite_id, filters)` — запустить run
  - `get_case_history(case_id)` — история запусков
  - `link_bug(result_id, bug_short_name)` — связать баг
  - `search_checklists(query)` — найти reusable checklist templates
  - `get_run_results(run_id)` — результаты run со статусами

### Tech Docs + RAG
- [ ] **Tech Docs хранилище** — документация по проекту, который тестируется
  - Хранить как отдельную сущность `TechDoc` (space_id, title, content, source_url)
  - Поддержка Markdown / HTML / Confluence import
  - Версионирование tech docs
- [ ] **pgvector** — векторное расширение PostgreSQL
  - Векторизовать: test cases (title + text + steps), suites, sections, tech docs
  - Embeddings через OpenAI / local model (text-embedding-3-small или nomic-embed-text)
  - Semantic search по всему контенту space
- [ ] **RAG Pipeline**
  - При создании нового кейса → ИИ ищет похожие существующие + релевантные tech docs
  - При ответе на вопрос "есть ли тест на X?" → semantic search
  - При генерации steps → ИИ читает tech docs по фиче
- [ ] **AI Assistant UI**
  - Чат-виджет в правом нижнем углу (или side panel)
  - Контекст: текущий suite / section / case
  - Команды: 
    - "Создай тест-кейс для [фича] на основе документации"
    - "Найди похожие кейсы на этот"
    - "Сгенерируй чеклист для [фича]"
    - "Какие тесты падают чаще всего?"

---

## 📋 Test Plan
- [ ] **Test Plan сущность** — промежуточный слой между Suite и Run
  - Plan = выборка кейсов из suite(s) с фильтрами
  - Один Plan → много Runs
  - UI: создание plan, выбор suites/секций/типов, environment, milestone
  - Run создаётся из Plan, а не напрямую из Suite
- [ ] **Run History** — на странице Test Case таб "Runs" со всеми запусками и статусами
- [ ] **Step-level результаты** — при прохождении Run можно отметить статус каждого шага (pass/fail/skip для каждого step)

---

## 🐛 Defects / Bugs
- [ ] **Defects Dashboard** — страница со всеми багами, связанными с ранами
  - Группировка по статусу (Open, Fixed, Reopen)
  - Статистика: количество багов по run/suite
  - Авто-связь fail → создание бага
- [ ] **Bug modal** при failed результате — быстрое создание бага с заполнением шагов, expected, actual

---

## 📊 Analytics / Dashboard
- [ ] **Dashboard page** — общая статистика space
  - Trend chart (passed/failed over time)
  - Top failed cases (какие кейсы чаще всего падают)
  - Coverage by suite/section
  - Runs count / duration
- [ ] **Suite coverage** — сколько % кейсов automated vs manual

---

## 🎯 Suite / Case UX Improvements
- [ ] **Drag-and-drop reordering** для секций (v-treeview DnD)
- [ ] **Inline rename** секции (двойной клик → поле ввода)
- [ ] **Search/filter** по секциям в дереве
- [ ] **Case counter** в узлах дерева: `Section Name (12)`
- [ ] **Duplicate test case**
- [ ] **Move case to section** (drag из списка в дерево или modal)
- [ ] **Compare versions** — side-by-side diff двух версий кейса
- [ ] **Tags / Priority** для кейсов (filterable, searchable)
- [ ] **Auto-save draft** при редактировании кейса
- [ ] **Command palette** — быстрый поиск по кейсам/суитам (Cmd+K)

---

## 🔧 Global UX
- [ ] **Breadcrumbs** — Space > Suite > Section > Case
- [ ] **Toast notifications** — Created / Updated / Deleted / Saved
- [ ] **Mobile responsive** — адаптивные таблицы, скрытие колонок
- [ ] **Keyboard shortcuts** — Cmd+K (search), Cmd+S (save), Esc (close modal)
- [ ] **Empty states** — иллюстрации + CTA для всех пустых экранов
- [ ] **Loading skeletons** — вместо spinner для таблиц

---

## ⚙️ Backend
- [ ] **Test Plan endpoints** (CRUD + filter cases)
- [ ] **Step-level results** модель + endpoint
- [ ] **Run History** endpoint для конкретного кейса
- [ ] **Analytics aggregations** (counts by status over time)
- [ ] **Full-text search** по description/steps (PostgreSQL tsvector)
- [ ] **Import/Export** — CSV/JSON для suites/cases
- [ ] **Tech Docs endpoints** — CRUD для документации по проекту
