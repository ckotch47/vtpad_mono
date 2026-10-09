# Desktop in-space navigation correction package r2

## Status

- Revision: `r2`
- Status: implemented and Docker-verified
- Supersedes the header-navigation interpretation in `plans/ui-navigation-and-list-affordances-package-r1.md`; the already implemented row links and Cases/Plans toolbar work remain in place
- Evidence: current `vtpad_front_v2/src/App.vue`, `src/layouts/spaces.vue` and route `tabValue` metadata inspected on 2026-10-09
- Scope: desktop navigation hierarchy only
- Mobile and mobile-specific implementation/testing remain excluded by user instruction
- User approved this exact revision with “делай” on 2026-10-09

## Outcome

Correct the desktop top bar to show navigation **inside the current Space**—Dashboard, Test Suites, Test Cases, Test Runs, Test Plans, Tech Docs and Bugs—instead of showing a list of Spaces. Keep the drawer as the place to switch between Spaces, and keep the profile in the top bar.

## Confirmed source findings

| ID | Finding | Evidence |
|---|---|---|
| NAV-R2-01 | The current top bar renders each Space as a tab linking to that Space's Dashboard. This is the wrong navigation level for the requested change. | `vtpad_front_v2/src/App.vue` |
| NAV-R2-02 | The existing `spaces` layout already defines the requested in-Space tabs and route destinations. It tracks active state through `route.meta.tabValue` and `route.params.spaceId`. | `vtpad_front_v2/src/layouts/spaces.vue`; primary Space route page metadata |
| NAV-R2-03 | `App.vue` currently fetches the Spaces list solely to render those top-bar Space tabs; the drawer independently continues to render the Space switcher. | `vtpad_front_v2/src/App.vue`; `leftAsideMain/SpacesListComponent.vue` |

## Implementation scope

1. Replace the top-bar list of Space names with the existing in-Space navigation destinations: Dashboard, Test Suites, Test Cases, Test Runs, Test Plans, Tech Docs and Bugs. Use the current `spaceId` and each route's `meta.tabValue` so detail routes keep the correct section active.
2. Render these tabs only on the primary Space section routes that use the existing `spaces` layout. Do not show them on auth, public, company, profile, Space settings, or report routes unless those routes already belong to that primary section layout.
3. Remove the duplicate tab strip from `src/layouts/spaces.vue` after moving it into the shared top bar. Preserve its current labels, order, route targets and active-tab behavior.
4. Remove the top-bar Spaces-list fetch and the Space-name tabs from `App.vue`. Keep the Spaces list/search in the drawer, the drawer toggle, and the compact profile menu in the desktop top bar.
5. Preserve SPA navigation and Vue reactivity; changing a section or opening/closing the drawer must not cause a full-page reload. Do not change API/data behavior or other list work from r1.
6. Update `project-docs/docs/architecture/codebase-map.md` and the desktop UI regression checklist to describe the corrected hierarchy and verification.

## Out of scope

- Changes to full-row links in Suites/Cases/Plans/Runs or Cases/Plans filters and create actions from r1.
- Mobile layouts and mobile-specific implementation/testing.
- Backend/API, database, permission, search or route-contract changes.
- Changes to the contents or ordering of the Spaces drawer.
- Redesign of separate Space settings/report tabs or company/profile tabs.

## Acceptance criteria

- On authenticated desktop primary Space routes, the top bar shows Dashboard, Test Suites, Test Cases, Test Runs, Test Plans, Tech Docs and Bugs for the current `spaceId`; it does not show other Space names as tabs.
- The active section tracks `route.meta.tabValue` on both list and detail routes.
- Choosing a section keeps the current Space and uses Vue Router without a full-page reload. The Space drawer still switches to another Space.
- Profile, notifications, company-admin navigation and the drawer toggle remain available.
- Company, profile, auth/public, settings and report pages do not show the primary Space-section tab strip.
- The desktop Docker build succeeds and the rebuilt frontend responds locally. Browser/keyboard checks are recorded only if run; unavailable checks are marked `not_run`.
- Relevant documentation is updated and the correction is committed separately.
- No mobile behavior is changed or claimed as verified.

## Approval

Approved by the user on 2026-10-09.

## Execution result

- Moved the seven current-Space section tabs into the shared desktop header and bound them to `route.params.spaceId` and `route.meta.tabValue`.
- Removed duplicate tabs from the `spaces` layout and removed the Space list request used only by the old header tabs. Space switching stays in the drawer.
- Updated the codebase map and desktop UI regression checklist.
- `git diff --check`: passed.
- Docker: `docker compose -f docker-compose.app-only.yml up -d --no-deps --build frontend` completed successfully; `vtpad_frontend_app` was recreated and started.
- Browser/keyboard checks: `not_run` per the requested Docker-only verification workflow. Mobile behavior was not changed or checked.
- Build output retained existing Sass legacy API deprecation notices and the existing large-chunk warning; the Vite production build completed successfully.
