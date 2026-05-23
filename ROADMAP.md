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
