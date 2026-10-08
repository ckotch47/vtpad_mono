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
- [x] Keep run result groups visible in a sticky left navigator on desktop and compact horizontal navigation on mobile
- [x] Redesign the run summary into progress/status, case-time, and shared-timer sections

RN1/RN2 passed frontend lint/build and desktop/mobile browser checks: the left navigator stayed visible during a long scroll, keyboard focus and result deep-link worked, and mobile had no page-wide horizontal overflow.

RDU2 polish is implemented in the approved full roadmap package and committed as `0a6e798`: the sticky run map uses clearer suite/section hierarchy, highlights the group in view, and shows the active group; summary progress, statuses, and time measurements share one card. Desktop and 390×844 mobile smoke passed on a read-only run, including long-scroll stickiness, group navigation/focus, and no page-wide overflow. Unknown case time with zero measured cases displays as “No data”; actual measured zero stays distinct. Independent code review passed.

### Test Plan & Execution
- [x] **Test Plan** entity — intermediate layer between Suite and Run
- [x] **Step-level results** — mark pass/fail/skip per individual step
- [x] **Run History** tab on Test Case page
- [x] **Bug modal on failed result** — quick bug creation with pre-filled data
- [x] Estimated execution time on test cases; estimate is versioned and snapshotted into runs
- [x] Actual case duration is editable in run results; `NULL` means unmeasured and `0` is valid
- [x] Run stats show the sum of measured case durations and measured/unmeasured counts
- [x] Shared run timer with pause/resume; active, paused, and calendar duration appear in run details and case history

TE1–TE5 passed manual REST and MCP runtime checks against a disposable database restored from the pre-apply backup. Startup applied v13/v14; estimates and actual durations distinguish `NULL`, `0`, and positive values; negative values are rejected; run snapshots remain stable; history/aggregates reconcile; pause time is excluded from active time; concurrent Resume requests leave one open interval. A browser smoke on the disposable clone verified Start, Pause, and Complete display the corresponding timer states and final durations; the Resume control remains unverified in browser. The project has no automated test suite.

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

### Suite and Case UX
SU1 and SU3 are implemented in code under approved plan r1: suite list/detail share a URL-backed split workspace with a flat searchable navigation list. Frontend lint/build and independent review passed; browser history and mobile interaction checks remain outstanding.
SU2 is implemented in code under approved plan r1: case search is scoped to the selected section, treats clearable `null` as an empty query, and distinguishes empty, no-match, loading, and request-error states. Frontend checks passed; browser interaction remains outstanding.

- [x] Redesign the suites screen to keep the suite list on the left and show the selected suite on the same page
- [x] Fix the case filter in suites: normalize clearable input, filter within the selected section, and distinguish empty/error states
- [x] Explore a Tech Docs-style tree structure for browsing test suites; use a flat searchable list because suites have no parent hierarchy
- [x] Reorder sections within the same parent through REST, MCP, drag-and-drop, and keyboard controls
- [x] Add search/filter for sections in the tree
- [ ] Move cases between sections by drag-and-drop or from a dialog
- [ ] Compare two test case versions side by side
- [ ] Add filterable and searchable tags and priority for cases

SU5 section filtering is implemented in `74fad6f`: matching sections retain their ancestors and order, selection survives filtering, and hidden-selection, no-match, and clear states are explicit. ESLint, production build, and `git diff --check` passed. Read-only desktop smoke on the local app verified a matching result, preserved hidden selection, no-match state, and clearing. Nested-section layout, keyboard focus, and mobile smoke remain in the regression checklist.

### Test Cases and Checklists
The TC2 Test IT review is complete. TC1 implementation is committed as `ade63d8`; lint/build and browser acceptance on a disposable clone passed. Checklist hidden fields survived type-switch/save, version history, mixed-run preview, and snapshot creation.
- [x] Design distinct views for test cases and checklists
- [x] Review how Test IT presents checklists and use the findings to inform the VTPad design

### Defects Dashboard
- [x] Add a space-level dashboard for bugs linked to test results
- [x] Group and filter defects by status (Open, Fixed, Reopen; retain an Other group)
- [x] Show defect statistics by run and suite
- [x] Provide explicit quick create-and-link from failed results; changing status alone does not create a bug

DD5 REST/MCP and browser acceptance passed on a disposable DB clone. Cancel and invalid title created no bug/link/receipt; explicit submit displayed the created bug and wrote one failed-result link plus one idempotency receipt. Status-only failure did not create a bug. Browser retry after transient network loss was not fault-injected; browser checks were desktop-only.

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
