# VTPad Roadmap

## ✅ Completed

### Core Test Management
- [x] Test Suite / Section / Test Case / Test Run / Test Result models
- [x] Server-side pagination, sorting, search for Cases, Suites, Runs
- [x] URL query params sync (page, search, sort, filters)
- [x] Bulk actions: delete + change status for Cases
- [x] Tiptap editor for description, preconditions, steps, expected_results
- [x] Test Case versioning (version snapshots)
- [x] Linked bugs for Test Results
- [x] Test Run results grouped by section
- [x] Stats cards in Suite Detail (total, manual, checklist, automated)
- [x] Section tree with context menu (add sub-section, rename, delete)
- [x] Add existing test cases to section
- [x] Test Case view modal from Suite Detail

### Test Plan & Execution
- [x] **Test Plan** entity — intermediate layer between Suite and Run
- [x] **Step-level results** — mark pass/fail/skip per individual step
- [x] **Run History** tab on Test Case page
- [x] **Bug modal on failed result** — quick bug creation with pre-filled data

### AI Integration (Completed)
- [x] MCP Server (33 tools) — embedded in FastAPI
- [x] Tech Docs storage with tree hierarchy
- [x] pgvector + HNSW index for semantic search
- [x] Embeddings via nomic-embed-text (768d)
- [x] Semantic search across cases, suites, sections, tech docs

### Dashboard & Analytics
- [x] **Dashboard page** — space-wide stats, trend chart, top failed cases, coverage
- [x] **Suite coverage** — automated vs manual percentage
- [x] Analytics endpoints (space stats, trend, top-failed, coverage)

### UX Improvements
- [x] Case counter in section tree nodes (`Section Name (12)`)
- [x] Duplicate test case
- [x] Inline rename section (double-click)
- [x] Auto-save draft when editing case
- [x] Breadcrumbs — Space > Suite > Section > Case
- [x] Toast notifications (vue3-toastify)
- [x] Command palette (Cmd+K)

---

## 🚧 In Progress / Planned

### Defects Dashboard
- [ ] **Defects Dashboard page** — all bugs linked to test results in space
- [ ] Group/filter by status (Open, Fixed, Reopen)
- [ ] Stats by run/suite
- [ ] Auto-link fail → bug creation (partially done via bug modal)

### Suite / Case UX Improvements
- [ ] Drag-and-drop reordering for sections
- [ ] Search/filter sections in tree
- [ ] Move case to section (drag or modal)
- [ ] Compare versions — side-by-side diff of two case versions
- [ ] Tags / Priority for cases (filterable, searchable)

### Global UX
- [ ] Keyboard shortcuts — Cmd+S (save), Esc (close modal)
- [ ] Loading skeletons for tables
- [ ] Empty states with illustrations + CTA for all screens
- [ ] Mobile responsive improvements

### Backend
- [ ] Full-text search via PostgreSQL tsvector
- [ ] Import/Export — CSV/JSON for suites/cases
- [ ] Tech Docs endpoints — full CRUD

---

## 📋 Future Ideas

- Test Plan advanced filters (by tags, priority, custom fields)
- Run comparison / diff between two runs
- Test automation integration (CI/CD webhooks)
- Requirements traceability matrix
- Custom fields for test cases
- Test case templates
- Notifications for run completion
- Email reports
- Public share links for runs
