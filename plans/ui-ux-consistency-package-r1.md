# UI/UX consistency package r1

## Status

- Revision: `r1`
- Status: implemented; desktop acceptance recorded on 2026-10-09 with documented not-run states
- Scope: desktop UI consistency and usability fixes based on the read-only UIX audit at source `486abba`
- Mobile layout and mobile-specific implementation/testing are excluded
- No implementation is authorized until this exact revision is approved

## Outcome

Make the audited VTPad desktop screens easier to understand and navigate by applying a small shared set of presentation and accessibility conventions, and fix the confirmed inconsistencies below.

This package does not claim a full product-wide design-system redesign. The audit had partial coverage, so the first pass is limited to confirmed issues and the screens observed by the tester. Broader visual changes require their own audited scope.

## Confirmed findings

| ID | Priority | Finding | Evidence |
|---|---|---|---|
| UIX-001 | High | Run detail combines `Untracked`, a calendar duration of `3172h 47m`, and “Timer measurements are unavailable.” The calendar value may represent real wall-clock elapsed time, so the UI must distinguish calendar duration from measured active/paused time instead of treating them as interchangeable. | Existing ACTIVE run detail, AX tree and screenshot |
| UIX-002 | Medium | The floating Spaces toggle overlaps the first visible Space row when the drawer is open; the accessibility tree also contains null and repeated Space names. | Global shell screenshot and AX tree |
| UIX-003 | Medium | Test Cases toolbar filter labels are visibly truncated (`Se...`, `Sta...`, `T`) at the inspected desktop width. | Test Cases list screenshot; accessible labels remain full |
| UIX-004 | Medium | Tech Docs shows “Create first page” even while the tree already contains documents. | Tech Docs screenshot and AX tree |
| UIX-005 | Low | Some icon-only actions in testcase rows and Tech Docs lack accessible names. | Test Cases and Tech Docs AX trees |

The tester's overall verdict was `fail`, with partial coverage. Test Case edit, Test Plan detail, Test Runs list, Bugs detail, keyboard-only focus, and forced loading/error states were not completed because the browser surface became unavailable. These are explicit retest gaps, not inferred passes.

## Implementation scope

1. **Run time summary**
   - Present wall-clock/calendar duration separately from tracked active and paused time.
   - When tracking data is unavailable, label that limitation next to active/paused time without implying a valid calendar duration is missing or measured work time.
   - Keep Vue state reactive; do not add a polling loop, cron, or page reload. Derive displayed values from existing reactive run/timer data and server timestamps.

2. **Spaces navigation**
   - Avoid covering a Space row with the floating toggle while the drawer is open; use the drawer's existing close control in that state.
   - Give null/blank Space names a stable readable fallback and make filtering null-safe.
   - Do not invent identity suffixes for repeated names. If existing UI data exposes a safe distinguishing field, show it only where it resolves an observed ambiguity; otherwise preserve the name and record that limitation.

3. **Test Cases filters**
   - Reflow the desktop toolbar so filter labels remain understandable at the inspected desktop width.
   - Preserve current filter behavior, selection state, and keyboard access.

4. **Tech Docs empty state**
   - Use wording that reflects whether the tree is empty. When pages already exist, invite selection or offer a neutral “Create page” action; use “Create first page” only when no page exists.

5. **Icon-only action accessibility**
   - Add concise accessible names and visible tooltips to the confirmed icon-only actions in Test Cases and Tech Docs.
   - Preserve existing action behavior and avoid adding decorative text to dense rows.

6. **Shared conventions for the touched screens**
   - Keep a consistent page hierarchy: title/context, primary action, then content.
   - Keep search and filters grouped with readable labels; use consistent spacing and status/empty-state language across touched screens.
   - Make keyboard focus visible on the changed controls.
   - Do not perform broad typography, color, or layout redesign beyond what is needed to satisfy these conventions on the touched screens.

## Out of scope

- Mobile or responsive-specific changes and mobile smoke tests.
- A whole-application redesign or a new component library/design token migration.
- Changes to timer storage, backend APIs, database schema, or run timing semantics.
- Changing how calendar duration is calculated without evidence that the underlying value is incorrect.
- Fixing unrelated testcase, suite, analytics, or Tech Docs behavior not in the findings above.

## Documentation

If implementation is approved, update the relevant existing documents under `project-docs/docs/` alongside the code. At minimum, document the clarified run time summary in the run lifecycle flow; update common errors only if the change resolves a documented limitation. Keep the documentation scope tied to actual behavior changes.

## Acceptance criteria

- Run summary no longer conflates calendar duration with tracked active/paused work time; unavailable tracking is clear and does not hide a valid calendar duration.
- Timer display updates reactively from existing state and does not reload the page or introduce periodic polling.
- Open Spaces navigation has no toggle overlay on its first row; blank names render a readable fallback and filtering does not throw.
- Test Cases filter captions remain identifiable at the audited desktop viewport; filters retain their prior behavior.
- Tech Docs empty-state wording matches whether pages exist.
- Every touched icon-only action exposes an accessible name and tooltip; changed controls have visible keyboard focus.
- Desktop browser retest records actual outcomes for each changed finding. A separate retest covers the currently blocked Test Case edit, Test Plan detail, Test Runs list, Bugs detail, keyboard focus, and loading/error/empty states where a safe fixture/state is available.
- Frontend lint/build and `git diff --check` pass; update the relevant project docs; commit each completed vertical fix/package as instructed by the user.
- Record any environment-blocked check as `not_run`/`blocked`; do not report an overall pass while high/medium failures remain.

## Proposed delivery order

1. Fix run time summary semantics and validate the existing reactive behavior.
2. Fix Spaces drawer overlap and null-name handling.
3. Reflow Test Cases desktop filters.
4. Correct Tech Docs empty-state wording and icon-action names/tooltips.
5. Run the desktop acceptance matrix, update documentation, and record remaining gaps.

## Approval

Implementation requires explicit user approval of `UI/UX consistency package r1`.
