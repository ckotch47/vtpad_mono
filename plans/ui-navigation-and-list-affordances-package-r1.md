# Desktop navigation and list affordances package r1

## Status

- Revision: `r1`
- Status: implemented; Docker rebuild and runtime smoke passed; desktop browser UX retest not run by user instruction
- Evidence: source inspection of the shared Vue shell, Suites, Cases, Plans and Runs lists on 2026-10-09; informed by the desktop UI/UX audit in `.memory/result/20261009T011352Z-desktop-uiux-audit.md`
- Scope: desktop shared navigation plus list interaction for Test Suites, Test Cases, Test Plans and Test Runs; list toolbar for Cases and Plans
- Mobile and mobile-specific implementation/testing are excluded by explicit user instruction
- No implementation is authorized until the user approves this exact revision

## Outcome

Make list navigation discoverable across the four requested modules, restore a compact shared header that includes Spaces navigation and the user profile, and give Cases/Plans a clear, usable filter and create-action area. Preserve Vue reactivity and current API/filter behavior.

## Confirmed source findings

| ID | Finding | Evidence |
|---|---|---|
| NAV-01 | Cases, Plans and Runs expose a router link only around the title text, so the rest of the row is not a navigation target. | `vtpad_front_v2/src/components/test-cases/testCasesListComponent.vue`; `test-plans/testPlansListComponent.vue`; `test-runs/testRunsListComponent.vue` |
| NAV-02 | Suite entries are `v-list-item`s, but only the name inside each item is a router link; clicking the remaining item area does not open the suite. | `vtpad_front_v2/src/components/test-suites/testSuitesListComponent.vue` |
| NAV-03 | The authenticated shared `v-app-bar` is 56px high and contains only the closed-drawer menu button. The profile and Spaces list are both inside the drawer. | `vtpad_front_v2/src/App.vue`; `leftAsideMain/ProfileLeftComponent.vue`; `leftAsideMain/SpacesListComponent.vue` |
| NAV-04 | Cases filters use two rows inside the shared outlined toolbar, with several wide/select-chip controls; Plans has only a search field in the same toolbar and places its create button in the action slot. | `vtpad_front_v2/src/components/common/ListPageToolbar.vue`; `test-cases/testCasesListComponent.vue`; `test-plans/testPlansListComponent.vue` |

## Implementation scope

1. Make the primary content area of each Suites, Cases, Plans and Runs list entry navigate to its existing detail route. Use a semantic router link with an accessible name and keyboard focus. Keep row-level buttons, selection checkboxes and other interactive controls independently usable; activating them must not navigate the row. Preserve existing route formats and current list data behavior.
2. Rework the authenticated desktop app bar into a compact shared navigation row: retain a visible drawer toggle, show the user's current Spaces as horizontal navigation tabs, and move the profile entry/actions into the bar as a compact profile control/menu. Keep the drawer available for finding and managing Spaces. Preserve notifications and company-admin navigation. Handle overflow without covering page content or hiding the active Space. Public/auth routes remain unaffected.
3. Redesign the list-level Cases and Plans filter/action presentation. Give search and filters a clear visual grouping, readable widths and labels, and place the primary create action where it is easy to find without dominating the filter controls. Cases retains its existing Type, Status, Priority, Tags and Suite filters; Plans retains its existing search behavior. Keep selection/bulk actions available and visually secondary to creating a case.
4. Reuse and refine `ListPageToolbar` or introduce only the smallest shared presentation primitive that serves these two pages. Avoid a broad redesign of other list modules.
5. Preserve all Vue-managed state transitions. Drawer toggle, active Space changes, filters, row navigation and create-dialog opening must not trigger a full-page reload when Vue Router/client-side state can handle the interaction. Do not add timers, polling, dependencies or backend changes.
6. Update the desktop UI regression checklist and relevant `project-docs/docs/` navigation/UI guidance to describe the final interactions and verification evidence.

## Out of scope

- Mobile layouts and mobile-specific implementation or testing.
- Backend/API, database, timer, filter semantics, permissions or search behavior changes.
- Reworking the contents or ordering of Spaces, or changing Space routes.
- Redesigning create dialogs or PlanCaseFilters internals; this package covers list-level filters and create-action placement.
- Restyling Bugs, Dashboards, Tech Docs or other list pages beyond any shared shell impact required for the app bar.

## Acceptance criteria

- At desktop viewports `1276×718` and `1440×900`, a click anywhere in the non-action portion of a Suite, Case, Plan or Run entry opens its existing detail route. The link is keyboard reachable and has an accessible name.
- Suite/Case/Plan/Run row actions and Cases selection controls remain operable and do not activate row navigation; no nested interactive elements are introduced.
- On authenticated desktop routes, the compact app bar keeps the drawer toggle visible and includes Space tabs plus a profile control. The current Space is identifiable; additional Spaces remain reachable when they exceed available width.
- The profile control preserves profile access, notifications and company-admin navigation. The drawer remains usable for searching and managing Spaces.
- Cases filters and create action have a clear hierarchy with no overlap, clipped labels or accidental wrapping at the listed desktop viewports. Existing filter values and result behavior remain unchanged.
- Plans search and create action are easy to identify in the same toolbar hierarchy; search debounce, clearing and result behavior remain unchanged.
- Pointer and keyboard checks confirm client-side navigation and reactive state updates without a full-page reload. No route state is lost when opening/closing the drawer or switching Spaces.
- Desktop browser verification records screenshots or equivalent rendered evidence and keyboard outcomes for the four list routes and shared header. Any unavailable state is marked `not_run`; no mobile claim is made.
- Relevant documentation is updated; targeted frontend lint/build and `git diff --check` pass; the completed package is committed as one coherent change.

## Approval

Approved by the user on 2026-10-09.

## Execution result

- Approved by the user on 2026-10-09.
- Desktop header and profile changes: commit `790c7bb` (`feat(ui): add spaces and profile to desktop header`).
- List navigation, Cases/Plans filter layout, and regression documentation: commit `6432fdf` (`feat(ui): improve desktop list navigation and filters`).
- `git diff --check`: passed before commits.
- Docker: `docker compose -f docker-compose.app-only.yml up -d --no-deps --build frontend` completed successfully; only `vtpad_frontend_app` was recreated.
- Runtime smoke: `vtpad_frontend_app` reported `Up`; `GET http://127.0.0.1:3000/` returned HTTP 200.
- Desktop browser interaction/visual retest: not run, per user instruction to rebuild Docker without a separate test environment.
- Mobile-specific work and checks: excluded.
