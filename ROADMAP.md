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
- [x] Reorder sections within the same parent through REST, MCP, drag-and-drop, and keyboard controls
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
All five time-tracking items (TE1–TE5) are implemented and runtime-verified under approved plan r2. The timer is shared across the run, and case duration is entered manually. Timer values are computed by the server from stored interval boundaries when requested; no cron, background loop, or client-side ticking is used. Manual REST and MCP checks passed against a disposable database restored from the pre-apply backup: startup applied v13/v14, estimates and actual durations distinguish `NULL`, `0`, and positive values, negative values are rejected, run snapshots remain stable, history/aggregates reconcile, and pause/resume excludes paused time. Concurrent Resume requests left one open interval. The timing UI was not browser-smoke-tested; there is no automated test suite.

### Run Navigation
RN1 and RN2 are verified under approved plan r1. Frontend lint/build and browser desktop/mobile checks passed, including focusable result navigation, sticky left group list through a long scroll, result deep-link, and no page-wide horizontal overflow. The summary now separates progress/status, measured case duration, and the shared timer without changing values.
- [x] Keep run result groups visible in a sticky left navigator on desktop and compact horizontal navigation on mobile
- [x] Redesign the run summary into progress/status, case-time, and shared-timer sections

### Suite and Case UX
SU1 and SU3 are implemented in code under approved plan r1: suite list/detail share a URL-backed split workspace with a flat searchable navigation list. Frontend lint/build and independent review passed; browser history and mobile interaction checks remain outstanding.
SU2 is implemented in code under approved plan r1: case search is scoped to the selected section, treats clearable `null` as an empty query, and distinguishes empty, no-match, loading, and request-error states. Frontend checks passed; browser interaction remains outstanding.

- [x] Redesign the suites screen to keep the suite list on the left and show the selected suite on the same page
- [x] Fix the case filter in suites: normalize clearable input, filter within the selected section, and distinguish empty/error states
- [x] Explore a Tech Docs-style tree structure for browsing test suites; use a flat searchable list because suites have no parent hierarchy
- [x] Reorder sections within the same parent through REST, MCP, drag-and-drop, and keyboard controls
- [ ] Add search/filter for sections in the tree
- [ ] Move cases between sections by drag-and-drop or from a dialog
- [ ] Compare two test case versions side by side
- [ ] Add filterable and searchable tags and priority for cases

### Test Cases and Checklists
- [ ] Design distinct views for test cases and checklists
- [ ] Review how Test IT presents checklists and use the findings to inform the VTPad design

### Defects Dashboard
- [x] Add a space-level dashboard for bugs linked to test results
- [x] Group and filter defects by status (Open, Fixed, Reopen; retain an Other group)
- [x] Show defect statistics by run and suite
- [ ] Extend automatic bug linking on failed results (partially available through the bug modal)

DD1–DD3 use stable UUID links only. The dashboard reports unique bugs separately from result links, groups by run and historical suite snapshot, bounds each bug's displayed navigation to 25 result links, and labels legacy JSON-only links as excluded. Runtime fixtures, cross-space isolation checks, browser smoke, API review, and security review passed on an isolated database copy. `EXPLAIN (ANALYZE, BUFFERS)` for the final paginated query on the restored clone took 1.584 ms with 231 shared-hit blocks and no shared reads; no index change was needed.

### Global UX
- [ ] Add keyboard shortcuts — Cmd+S to save and Esc to close a modal
- [ ] Add loading skeletons for tables
- [ ] Add empty states with illustrations and clear next actions
- [ ] Improve mobile responsiveness

### Backend and Data
- [ ] Add PostgreSQL full-text search with `tsvector`
- [ ] Add CSV/JSON import and export for suites and cases
- [x] Harden Tech Docs CRUD and traceability with space membership, same-space parent checks, and cycle protection

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
