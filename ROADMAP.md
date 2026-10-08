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

### Run Navigation
- [x] Group run results by suite and full nested section path; preserve the path in each run snapshot
- [x] Add quick navigation between result groups with filtered counts, keyboard focus, and responsive desktop/mobile layouts

### Test Plan & Execution
- [x] **Test Plan** entity — intermediate layer between Suite and Run
- [x] **Step-level results** — mark pass/fail/skip per individual step
- [x] **Run History** tab on Test Case page
- [x] **Bug modal on failed result** — quick bug creation with pre-filled data
- [x] Estimated execution time on test cases; estimate is versioned and snapshotted into runs
- [x] Actual case duration is editable in run results; `NULL` means unmeasured and `0` is valid
- [x] Run stats show the sum of measured case durations and measured/unmeasured counts
- [x] Shared run timer with pause/resume; active, paused, and calendar duration appear in run details and case history

### AI Integration (Completed)
- [x] MCP Server — embedded in FastAPI
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

### Test Execution Time
All five time-tracking items (TE1–TE5) are implemented in code under approved plan r2. The timer is shared across the run, and case duration is entered manually. Timer values are computed by the server from stored interval boundaries when requested; no cron, background loop, or client-side ticking is used. Automated tests, database migration, and Docker runtime checks remain outstanding.

### Run Navigation
RN1 and RN2 are implemented in code under approved plan r1. Static checks and production build passed; browser interaction and keyboard/mobile runtime checks remain outstanding.

### Suite and Case UX
SU1 and SU3 are implemented in code under approved plan r1: suite list/detail share a URL-backed split workspace with a flat searchable navigation list. Frontend lint/build and independent review passed; browser history and mobile interaction checks remain outstanding.

- [x] Redesign the suites screen to keep the suite list on the left and show the selected suite on the same page
- [ ] Fix the case filter in suites (it currently does not work)
- [x] Explore a Tech Docs-style tree structure for browsing test suites; use a flat searchable list because suites have no parent hierarchy
- [ ] Add drag-and-drop reordering for sections
- [ ] Add search/filter for sections in the tree
- [ ] Move cases between sections by drag-and-drop or from a dialog
- [ ] Compare two test case versions side by side
- [ ] Add filterable and searchable tags and priority for cases

### Test Cases and Checklists
- [ ] Design distinct views for test cases and checklists
- [ ] Review how Test IT presents checklists and use the findings to inform the VTPad design

### Defects Dashboard
- [ ] Add a space-level dashboard for bugs linked to test results
- [ ] Group and filter defects by status (Open, Fixed, Reopen)
- [ ] Show defect statistics by run and suite
- [ ] Extend automatic bug linking on failed results (partially available through the bug modal)

### Global UX
- [ ] Add keyboard shortcuts — Cmd+S to save and Esc to close a modal
- [ ] Add loading skeletons for tables
- [ ] Add empty states with illustrations and clear next actions
- [ ] Improve mobile responsiveness

### Backend and Data
- [ ] Add PostgreSQL full-text search with `tsvector`
- [ ] Add CSV/JSON import and export for suites and cases
- [ ] Harden existing Tech Docs CRUD with space membership and same-space parent checks

### Analytics — Later
- [ ] Expand analytics beyond the existing dashboard, suite coverage, and space-level statistics
- [ ] Use recorded case and run execution times for duration and trend analysis

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
