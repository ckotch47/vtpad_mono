# Test-case and Space tag unification package r1

## Status

- Revision: `r1`
- Status: implemented; exact revision r1 approved by user
- Scope: use the existing space tag catalog as the one canonical tag catalog for bugs and test cases
- User intent: “все верно, теперь их надо объядинить” (2026-10-09)
- Implementation requires approval of this exact plan revision under root `AGENTS.md`
- Project memory profile: local; scoped retrieval completed before planning

## Outcome

Test cases and Bugs use the same `TagModel` records in `tagmodel`, scoped to a Space. Existing space tags become selectable for test cases. A label entered while editing a case creates/reuses a regular Space tag, so it is also available in the existing Space tag manager and for Bugs. Keep `tags: string[]` in current case REST/MCP payloads and keep history/run snapshots label-based for compatibility.

## Confirmed findings

| ID | Finding | Evidence |
|---|---|---|
| TAG-U1-01 | Existing Space tags use `TagModel` (`tagmodel`) with `title`, `color`, and a Space FK; the existing UI and REST CRUD use these rows. | `vtpad_backend/app/src/tag/model.py`, `service.py`, `router.py`; `vtpad_front_v2/src/components/tags/tagsListComponent.vue`; `src/services/tagService.js` |
| TAG-U1-02 | Test-case tags currently use separate `test_case_tag` and `test_case_tag_link` tables created by v15; case label identity is Python `casefold()` within a Space. | `vtpad_backend/app/src/migration/data/v15_test_case_priority_tags.json`; `app/src/test_case/model.py`, `service.py` |
| TAG-U1-03 | The case tag API and MCP currently expose string labels, and the frontend case editor allows selecting existing labels or entering a new one. | `app/src/test_case/router.py`; `app/src/mcp/tools/test_cases.py`; `src/pages/space/:spaceId/test-cases/[caseId]/edit.vue`; `src/components/test-cases/testCasesListComponent.vue` |
| TAG-U1-04 | Raw SQL and projections also read case-specific tag tables for search, version snapshots, and data exchange. They must switch to the unified association source. | `app/src/test_case/service.py`; `app/src/data_exchange/service.py` |
| TAG-U1-05 | Existing `TagModel` has no uniqueness constraint for normalized titles, and legacy duplicate titles may exist. It also has colors and Bug associations that migration must preserve. | `app/src/tag/model.py`; `app/src/bugtags/model.py`; API/DB review |
| TAG-U1-06 | Generic Tag CRUD currently has REST endpoints but no equivalent generic-tag MCP CRUD tools. Case tag label operations are already exposed in MCP. | `app/src/tag/router.py`; `app/src/mcp/tools/test_cases.py` |
| TAG-U1-07 | Latest migration is v29; the runner applies JSON SQL migrations transactionally by default. | `app/src/migration/data/v29_public_run_links.json`; `app/migration.py` |

## Implementation scope

1. Make existing `TagModel` the canonical catalog. Add a test-case association table that references `tagmodel`; do not reuse the Bug-only association table.
2. Add a transactional v30 migration that backfills every current test-case tag link to a Space `TagModel` and the new association table:
   - Match within the same Space using trimmed, case-insensitive titles. Prefer an exact title match; when multiple existing rows match, select deterministically by oldest `create_date`, then ID.
   - Reuse matched rows without changing their IDs, colors, or Bug links.
   - If there is no match, create a regular Space tag with the old case label and `color = NULL`, then link the case to it.
   - Deduplicate repeated case/tag association pairs during transfer. Never merge, delete, recolor, or relink pre-existing generic tag rows or Bug associations in this package.
   - Keep old `test_case_tag` and `test_case_tag_link` tables as deprecated migration residue for this release; new code must stop reading/writing them. A later cleanup migration can drop them after cutover is established.
3. Replace `TestCaseTagModel` references with the shared `TagModel` association across create/update, list/detail serialization, all-tags filters, versions/restores, duplicates, run snapshots, plan filters, and import/export. Continue returning case `tags` as string labels; historical version and run snapshots remain immutable strings.
4. Keep the existing `GET /api/v2/test-case/space/{space_id}/tags` and MCP `list_test_case_tags` contracts as `list[str]`, but derive options from all tags in that Space (deduplicated by normalized title). This preserves current clients and makes unused Space tags selectable.
5. Preserve the case editor’s current free-entry behavior. When a case request supplies a new label, resolve it to an existing same-Space tag by normalized title or create a standard `TagModel` with no color. Enforce the existing `tags` capability for case writes and standard Tag CRUD; reject cross-Space tag IDs if any new internal/API path uses IDs.
6. Prevent new duplicate normalized tag titles through shared Tag CRUD and case tag resolution, using a consistent Space-level serialization strategy. Leave existing duplicate generic tag records intact; when linking a label with multiple matches use the deterministic rule in item 2 and report the ambiguous count during migration verification. Do not add a uniqueness constraint that can fail on existing data.
7. Add MCP parity for generic Space Tag CRUD (`list`, `create`, `update`, `delete`) with the same Space access and `tags` write capability checks as REST. Existing MCP case tag strings and tool signatures remain compatible.
8. Update API endpoint maps, MCP documentation, tag/case lifecycle and access documentation, and `ROADMAP.md` to record the unified model and completion status only after implementation evidence exists.
9. Keep the tag chips label-only in this package; displaying shared tag colors in the case UI is not required for data/API unification.

## Out of scope

- Deleting or coalescing existing generic Space tags with duplicate titles, or changing their colors/Bug links.
- Changing case REST/MCP payloads from `tags: string[]` to tag IDs or objects.
- Adding a DB uniqueness constraint across all existing `TagModel` rows.
- Redesigning tag UI or adding colored case chips.
- Deleting deprecated v15 tables in this cutover package.
- Any production deployment or external Tracker status update.

## Acceptance criteria

- Existing case labels are all represented by shared `TagModel` rows in the same Space, and every current case/tag association points to the shared catalog.
- Existing generic tag IDs, titles, colors, and Bug associations remain unchanged; no cross-Space case/tag links are created.
- Existing Space tags appear as options in case create/edit and test-plan tag filters. A new case-entered label appears in Space tag management and can be reused by Bugs.
- REST and MCP preserve case tag string contracts and enforce the same Space/capability boundaries for writes. Generic Tag CRUD is available through both REST and MCP.
- Filters, search, test-plan sourcing, version/restore, duplicate, run snapshots, and import/export resolve tags through the shared association; legacy snapshots retain their existing values/unknown semantics.
- Migration verification reports source link count, transferred distinct pair count, created/reused shared tag counts, ambiguous duplicate-title count, and confirms no unresolved or cross-Space links.
- Backend/frontend Docker builds succeed, the backend migration log confirms v30 applied once, and the local frontend/backend endpoints respond after container recreation. No disposable test environment is used, following the user's prior verification preference; database mutation is limited to the configured local application database after this plan is approved.
- Relevant docs and roadmap status are updated, and implementation is committed in a dedicated commit.

## Implementation evidence

- v30 applied and recorded in the configured local app database as `v30_unify_test_case_space_tags.json`.
- The local database had no legacy tag data at cutover: 0 rows in `test_case_tag`, 0 rows in `test_case_tag_link`, and 0 rows in `test_case_tag_link_shared`; post-migration cross-Space links and legacy labels without a generic Space match both count 0. Thus the migration path ran, but non-empty backfill behavior was not exercised against fixture data, consistent with the no-disposable-test-environment decision.
- `docker compose -f docker-compose.app-only.yml up -d --no-deps --build backend frontend` built both images; both containers were then force-recreated. Backend `/ready` and frontend `/` returned HTTP 200.
- `git diff --check` passed. Automated tests were not run; Docker startup validated module import/registration and applied the transactional migration.
- REST/MCP case contracts remain `tags: string[]`; generic MCP CRUD was registered in `app/src/mcp/tools/__init__.py`. API, lifecycle, access, error, MCP, architecture and roadmap docs were updated.

## Risks and decisions encoded in this revision

- Tag title normalization: current case tags use Python `casefold`; generic tags have no stored normalized field and PostgreSQL matching uses `lower(trim(title))`. This plan deliberately uses exact-title preference followed by trimmed case-insensitive matching, which is compatible for ordinary labels but may not equate all Unicode casefold pairs (for example, `ß` and `ss`). Such labels remain distinct rather than being silently merged.
- Duplicate generic tag titles are preserved. Case links resolve to the deterministic canonical match; existing duplicate rows remain available to existing Bug/tag-management behavior.
- Deleting a shared Space tag will remove current case and Bug associations according to the existing generic tag deletion behavior; version/run snapshots retain their string labels.
- The migration keeps the old v15 tables for rollback evidence but makes them non-authoritative. Backend cutover must recreate the backend as one version; do not run old and new backend code concurrently against the migrated schema.

## Approval

User approved this exact revision with “Да, одобряю r1” before implementation.
