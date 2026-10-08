# Test Case and Checklist UI — TC1 r1

Mode: full
Revision: 1
Lifecycle state: ready_for_approval
Approval: pending

## Outcome and priority

- **Outcome:** make checklist items visually and semantically distinct from full test cases across creation, editing, detail, and run execution views.
- **Success measure:** a checklist user sees its checks without test-case-only fields; a full test case retains description, preconditions, steps, and expected results. Existing content and run snapshots remain readable and unchanged.
- **Priority:** the VTPad roadmap calls out this UX gap, and the Test IT review confirms the difference in applicable fields.
- **Stakeholders and approver:** VTPad owner (user).

## Scope and constraints

### In

- Update the case library create dialog, case edit page, case detail page, and run result detail to present `checklist` separately from `manual` test cases.
- For a checklist, label `steps` as checks and present them in a compact list-oriented layout using existing rich-text content/editor capabilities.
- For manual cases, continue to present description, preconditions, steps, and expected results.
- Keep the existing shared case model, version snapshots, and run snapshot behavior. When a user switches type, hide type-inapplicable fields but preserve their stored values so switching back or reviewing an earlier version can reveal them.
- Keep a single result status for the whole checklist in a run. Checklist rows do not gain independent execution state in this package.
- Preserve the existing automated type behavior.
- Update relevant project documentation and `ROADMAP.md` after implementation.

### Out

- Backend/API or MCP contract changes, database migrations, per-check result persistence, and conversion workflows that move/transform content between types.
- Replacing the editor, adding dependencies, or creating independent routes for checklist items.

### Constraints and assumptions

- `TestCaseModel` stores `type`, `text`, `steps`, `preconditions`, and `expected_results` on one shared record; run snapshots include those fields. There is no per-check result model.
- Existing Tiptap editor supports task-list content; stored `steps` must not be rewritten as part of rendering.
- Checklist type switching changes presentation only. Values in hidden fields remain intact and are restored by the existing version/history mechanism.
- Test IT documentation is a design reference, not a compatibility target: checklist omits expected results and pre/postconditions while retaining checks and result history.

## Acceptance criteria

| AC | Criterion | Evidence required | Owner |
|---|---|---|---|
| AC-1 | Checklist creation/editing shows title, description, checks, and shared metadata; it omits preconditions and expected results. Manual case editing retains its applicable fields. | Browser smoke for create and edit flows; frontend lint/build. | Frontend Engineer |
| AC-2 | Checklist detail presents checks in a list-oriented view and does not show test-case-only sections. Manual detail retains its full scenario layout. | Browser smoke for both types, including empty and populated fields. | Frontend Engineer |
| AC-3 | Run detail identifies checklist items and displays their checks while retaining one result status for the whole item. | Browser smoke in a mixed run with one checklist and one manual case. | Frontend Engineer |
| AC-4 | Switching item type hides fields without clearing them; switching back restores them. Existing cases and snapshots remain readable. | Browser flow plus inspection of saved API payload/snapshot before and after switching. | Frontend Engineer |
| AC-5 | Responsive layout and keyboard use remain usable; type-specific fields have clear labels and accessible focus order. | Desktop/mobile browser smoke and keyboard interaction. | Frontend Engineer / QA |
| AC-6 | Relevant flow documentation and roadmap status match the shipped behavior. | Documentation diff review. | Technical Writer |

## Delivery DAG

| ID | Work package | Dependencies | Proposed role | Expected artifact | Applicable policies | Gate |
|---|---|---|---|---|---|---|
| WP-1 | Implement type-specific create/edit/detail/run views and verify stored-field preservation. | Exact r1 approval | Frontend Engineer | Vue changes and manual verification record | `frontend-engineering`, `implementation-delivery`, `manual-qa-risk-boundaries` | Lint, build, browser and keyboard/mobile smoke |
| WP-2 | Add a testcase lifecycle flow doc, link it from the docs index, update existing run flow if necessary, and mark TC1/TC2 in roadmap based on evidence. | WP-1 | Technical Writer (fallback: current workflow) | `project-docs/docs/flows/test-case-lifecycle.md`, `project-docs/docs/index.md`, and roadmap | Documentation Policy | Independent diff/evidence review |

## Risks and blockers

| ID | Risk/blocker | Impact | Owner | Mitigation/requested decision | Status |
|---|---|---|---|---|---|
| R-1 | Legacy checklist records may already contain preconditions or expected results. | Hiding them could look like data loss. | Frontend Engineer | Preserve values in the payload and verify toggling type restores visibility; do not clear values on save. | Open |
| R-2 | Rich-text checks may contain nested lists, tables, or existing task-list markdown. | A custom parser could corrupt or flatten content. | Frontend Engineer | Render through the existing editor/read-only path; do not parse or rewrite saved `steps`. | Open |
| R-3 | The run model stores one status per item. | Per-row checkboxes could imply unsupported persistence. | Product owner | Keep checks read-only in run detail; only the overall checklist result is actionable. | Resolved by plan |

## Evidence-based status

- Completed: TC2 research in `plans/roadmap-solutions-r1.md`; current shared model/editor and affected screens inspected.
- In progress: none.
- Blocked: implementation awaits explicit approval of this exact plan revision, required by root `AGENTS.md`.
- Next milestone: after approval, implement WP-1, run project-native checks and browser smoke, then complete WP-2.

## Policy checks

| Policy | Owner | Status | Evidence | Risks | Required action |
|---|---|---|---|---|---|
| Frontend engineering | Frontend Engineer | pending | Vue 3/Vuetify 3, shared Tiptap editor, existing screens inspected | Rich-text content preservation | Preserve and browser-check current editor path |
| Data/API compatibility | API Reviewer | not_applicable | Plan changes only presentation and keeps DTO/model shape | None expected | Revisit if implementation changes API or payload semantics |
| Security/privacy | Security Reviewer | not_applicable | No auth, access scope, or data exposure changes planned | None expected | Revisit if scope changes |

## Composite acceptance

| Role | Verdict | Evidence | Residual risks |
|---|---|---|---|
| Product Manager | pending | Owner approval and AC evidence required | Browser timing for run result UI |
| Frontend Engineer | pending | WP-1 implementation evidence required | Legacy rich-text presentation |
| Code Reviewer | pending | Independent implementation diff review required | None known |

## Traceability

| AC | Work package | Evidence | Required verdict | State |
|---|---|---|---|---|
| AC-1–AC-5 | WP-1 | Browser, lint, build, and saved-payload checks after implementation | Frontend + code review | not_started |
| AC-6 | WP-2 | Docs diff after implementation | Product acceptance | not_started |

## Stakeholder update

- Outcome status: plan ready; implementation not started.
- Delivered: exact r1 package and acceptance criteria.
- Evidence: current Vue screens/model/editor inspected; official Test IT docs reviewed.
- Blockers: exact plan approval required.
- Decisions needed: approve `plans/checklist-ux-package-r1.md` r1.
- Risks: checklist run results remain one overall status; no per-row execution tracking.
- Next milestone: implement after exact r1 approval.

## References

- Test IT, [Create work items](https://docs.testit.software/user-guide/sections/create-work-items.html).
- Test IT, [Compare work item types](https://docs.testit.software/user-guide/sections/compare-work-item-types.html).
- VTPad: `testCasesListComponent.vue`, `testCaseDetailComponent.vue`, `test-cases/[caseId]/edit.vue`, `testRunDetailComponent.vue`, and `TestCaseModel`.
