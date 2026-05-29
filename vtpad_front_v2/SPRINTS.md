# VTPad UI/UX Sprints

> Generated from UI/UX audit (49 issues). Prioritized by impact and effort.

---

## Sprint 0 — Critical Fixes ✅ DONE

### S0-1: Fix global CSS pollution in App.vue ✅
- **File:** `src/App.vue`
- **Fix:** Scoped `input`/`select` resets to exclude `.v-field__input`. Migrated hardcoded bug-state colors to Vuetify theme tokens.

### S0-2: Add alt text to all v-img components ✅
- **Files:** `ProfileLeftComponent.vue`, `settingsUserComponent.vue`, `bugsModalComponent.vue`, `bugsListRowComponent.vue`, `profileMainComponent.vue`

### S0-3: Add aria-label to icon-only buttons ✅
- **Files:** `testCaseDetailComponent.vue`, `testSuitesListComponent.vue`, `testSuiteDetailComponent.vue`, `tech-docs/index.vue`, `testRunsListComponent.vue`, `SpacesListComponent.vue`, `ProfileLeftComponent.vue`
- **Fix:** Added `aria-label` to 25+ icon-only v-btns.

### S0-4: Remove dead code / console.logs ✅
- **Files:** `companyUserListComponent.vue`, `bugsListComponent.vue`, `reportQaFilterComponent.vue`, `issue/:id/index.vue` + 7 more
- **Fix:** Commented out or replaced all active `console.error` calls.

### S0-5: Add form validation to all create/edit dialogs ✅
- **Files:** `environmentListComponent.vue`, `milestoneListComponent.vue`, `customFieldListComponent.vue`, `apiTokenListComponent.vue`, `testSuitesListComponent.vue`, `testCasesListComponent.vue`, `testPlansListComponent.vue`, `testRunsListComponent.vue`

### S0-6: Fix responsive bugs table ✅
- **File:** `src/components/bugs/bugsListComponent.vue`

### S0-7: Fix bug modal responsive width ✅
- **File:** `src/components/bugs/modal/bugsModalComponent.vue`

---

## Sprint 1 — UX & Error Handling ✅ DONE

### S1-1: Add global API error handling ✅
- **File:** `src/plugins/axios.js`
- **Fix:** Toast errors now readable (FastAPI detail parsing), duration 3s.

### S1-3: Add confirmation dialogs for destructive actions ✅
- **Files:** `environmentListComponent.vue`, `milestoneListComponent.vue`, `customFieldListComponent.vue`, `apiTokenListComponent.vue`

---

## Sprint 2 — Visual Consistency ✅ DONE

### S2-1: Migrate hardcoded colors to Vuetify theme tokens ✅
- **Files:** `editorComponent.vue`, `reportTestSpaceComponent.vue`, `collorList.js`

### S2-2: Fix dark mode support in editor ✅
- **File:** `src/components/common/editor/editorComponent.vue`

### S2-3: Create reusable PageHeader component ✅
- **File:** `src/components/common/pageHeaderComponent.vue`

### S2-4: Fix notification badge styling ✅
- **File:** `src/components/notifications/notificationRingsComponent.vue`

### S2-5: Fix editorComponent prop bug ✅
- **File:** `src/components/common/editor/editorComponent.vue`

---

## Sprint 3 — Accessibility & Polish ✅ DONE

### S3-3: Fix responsive layout issues ✅
- **Files:** `reportQaFilterComponent.vue`, `tech-docs/index.vue`

### S3-5: Add loading states ✅
- **Files:** `SpacesListComponent.vue`, `tech-docs/index.vue`

---

## Sprint 4 — Minor Cleanup ✅ DONE

### M1: Remove HelloWorld.vue scaffold leftover ✅
### M2: Fix 404 page grammar ✅
### M3: Remove mock data from aqaReportSelectComponent ✅
### M4: Fix invalid color prop usage ✅
### M5: Remove dead companyMainComponent ✅
### M6: Fix nested fluid containers ✅
### M7: Clean up console errors / alerts ✅

---

## Sprint 5 — A+B Additional Improvements ✅ DONE

### A2: Empty states for v-data-table-server ✅
- **Files:** `testRunsListComponent.vue`, `testCasesListComponent.vue`, `testSuitesListComponent.vue`, `testPlansListComponent.vue`, `testCaseDetailComponent.vue`
- **Fix:** Added `<v-empty-state>` to all 5 tables.

### A3: Loading states ✅
- **Files:** `dashboardComponent.vue`, `bugsListComponent.vue` (already had), `SpacesListComponent.vue`, `tech-docs/index.vue`

### A5: Keyboard focus visible states ✅
- **File:** `src/App.vue`
- **Fix:** Added `*:focus-visible { outline: 2px solid primary; outline-offset: 2px; }`

### B2: Inline sort editing ✅
- **Files:** `testSuitesListComponent.vue`, `testCasesListComponent.vue`
- **Fix:** Click on Sort column → inline number input → blur/enter saves via API.

### B4: Keyboard shortcuts help modal ✅
- **File:** `src/App.vue`
- **Fix:** Press `?` anywhere to open shortcuts help dialog.

---

## Summary
- **Total issues fixed:** 30+ из 49
- **All builds pass:** `npm run build` ✅
- **New features delivered:**
  - Inline sort editing for suites & cases
  - Keyboard shortcuts help (`?`)
  - Empty states for all data tables
  - Theme-aware editor + colors
  - Form validation everywhere
  - Responsive layouts
  - Toast notifications
