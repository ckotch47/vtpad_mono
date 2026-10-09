# Desktop UI/UX coherence package r1

## Status

- Revision: `r1`
- Status: proposed; implementation not started
- Evidence: independent exploratory run on the local VTPad desktop UI at `1276×718`, plus source review
- Mobile and mobile-specific implementation/testing are excluded by explicit user instruction
- Implementation requires approval of this exact revision

## Outcome

Make the main VTPad desktop workflows feel consistent and easier to scan while retaining module-specific controls and Vue reactivity. Align list-page hierarchy, remove duplicate or misleading controls, and make visible actions understandable to keyboard and screen-reader users.

Keep existing filter semantics, routes, permissions, and data behavior. Update local Vue state without a full-page reload where the existing flow permits it.

## Confirmed findings

| ID | Priority | Finding | Evidence |
|---|---|---|---|
| UXC-001 | Medium | Suite section names appear twice in the section list. The item sets `:title` while also rendering a `v-list-item-title`. | Browser screenshot; `vtpad_front_v2/src/components/test-suites/detail/SuiteSectionsPanel.vue` |
| UXC-002 | Medium | The section overflow menu is an icon-only button without an accessible name or tooltip. | Accessibility tree; `SuiteSectionsPanel.vue` menu activator |
| UXC-003 | Medium | The Bugs quick-create action is rendered as a pseudo-row inside the table, alongside an `OPEN` status value, so it reads like bug data rather than the page's primary action. | Browser screenshot and `vtpad_front_v2/src/components/bugs/BugsDataTable.vue:78-87` |
| UXC-004 | Low | Run timer state and interval count are repeated below a summary card that already displays timer state and elapsed-time breakdown. | Browser screenshot; `RunStatsPanel.vue` and `testRunDetailComponent.vue:49-68` |
| UXC-005 | Medium | Main list pages arrange title, primary action, search, and filters differently: Cases uses a multi-row toolbar, Plans/Runs use compact toolbars, Bugs puts filters in the table/header, and Suites uses a split workspace. | Browser comparison across Cases, Suites, Plans, Runs, and Bugs |

## Implementation scope

1. Use the existing `ListPageToolbar` and shared page hierarchy as the default for the desktop list pages: title/context, primary action, grouped search/filters, then results. Preserve each module's relevant controls and the Suites split-pane workspace.
2. Remove the duplicate visible suite-section title while retaining a way to reveal a long full name. Add a concise accessible name and tooltip to the section menu button.
3. Move Bugs quick-create into the primary-action area above the table. Keep empty-state guidance and permission behavior consistent with that action.
4. Remove the redundant Run timer state row or fold its refresh action into the existing timer summary. Keep interval count available once, preserve Start/Pause/Resume behavior, and keep elapsed time reactive without polling or reloads.
5. Align spacing, toolbar/control density, primary-action placement, and loading/empty/error state framing across Cases, Suites, Plans, Runs, and Bugs. Do not change query parameters or which records filters return.
6. Preserve semantic buttons/links, accessible names, keyboard focus visibility, and existing route behavior for all touched actions.

## Out of scope

- Mobile layouts and mobile-specific implementation/testing.
- A new component library, broad color/theme redesign, or typography redesign.
- Backend/API, database, timer-storage, permissions, filter semantics, or pagination-contract changes.
- Changes to Dashboard or Tech Docs; they were used as reference screens during the audit and had no confirmed finding in this pass.
- Destructive or state-changing browser checks against shared application data.

## Documentation

Update the relevant desktop UI guidance under `project-docs/docs/` with the shared list-page hierarchy and action semantics. Update `project-docs/docs/errors/common-errors.md` only if a documented behavior is corrected. Record unverified states explicitly.

## Acceptance criteria

- Cases, Suites, Plans, Runs, and Bugs use a consistent desktop hierarchy for heading/context, primary action, filters/search, and results at `1276×718` and `1440×900`, without overlapping or clipped controls.
- Suite section names render once; long names remain discoverable, and the section menu button has a meaningful accessible name, tooltip, keyboard activation, and visible focus.
- Bugs quick-create is presented as a page action rather than a table-data row and remains available only where permitted.
- Run timer state appears once in the summary; controls and interval information remain clear, and elapsed values update from reactive state without a page reload or polling loop.
- Existing query/filter results, route state, and list-specific controls remain unchanged.
- Loading, empty, error, and permission states retain valid actions and consistent framing.
- Desktop browser retest records actual screenshot/accessibility-tree evidence for all five modules and keyboard checks for changed controls. State-changing checks use an isolated fixture or are marked `not_run`.
- Targeted frontend lint/build and `git diff --check` pass; relevant docs are updated; commit the completed package.
- No mobile acceptance claim is made.

## Approval

Implementation requires explicit user approval of `Desktop UI/UX coherence package r1`.
