# FI9 — public links for test runs (r1)

Status: implementation complete; disposable runtime/browser acceptance performed; feature remains disabled pending external proxy/trace-log acceptance. Approved for implementation on 2026-10-09 after the user authorized completion of the full roadmap. This is the concrete delivery revision for the approved FI9 scope in `roadmap-completion-package-r3.md`.

## Product decisions for this revision

- The public view is a safe projection recalculated on each redemption from the run's stored testcase snapshots and current result statuses/durations. It is not a frozen copy from link creation.
- Each run can have one active link. Creating a replacement atomically revokes the previous link.
- Owners/creators may share runs in any lifecycle state. The public response reports the run's current status and only the fields explicitly listed below.
- The share secret is 32 CSPRNG bytes, returned once as a version-prefixed opaque bearer string. PostgreSQL stores only an HMAC-SHA-256 digest. The HMAC key is an HKDF-SHA-256 subkey derived from `SECRET_KEY` with FI9-specific salt/info and a stored key version. If the master key is unavailable or invalid, creation and redemption fail closed.
- Server feature flag `PUBLIC_RUN_LINKS_ENABLED` and frontend build flag `VITE_PUBLIC_RUN_LINKS_ENABLED` default to false. Security/leakage acceptance must pass before operators enable the feature.
- Public rate limits use shared Redis atomic increments: 30 requests/minute per share token and 120/minute per client IP. Redis failure rejects public redemption. IP comes from the ASGI client address under the configured trusted-proxy boundary; arbitrary forwarded headers are not read by application code.

## In scope

- PostgreSQL model/migration for run links, token digest/version, creator, creation/expiry/revoke timestamps, plus atomic rate-limit support if the existing Redis service cannot provide a suitable helper.
- One shared service for create, metadata read, revoke, and redemption. Create/revoke must re-read run ownership, current active space membership, same-company active status, and company role on every call. Permit the run creator or an active space owner; permit an active same-company `company_admin` only when also an active member of that space. For a run without `created_by`, only an active space owner can create/revoke.
- Authenticated REST create/status/revoke endpoints; unauthenticated REST redemption reads the opaque token only from `Authorization: Bearer ...`.
- MCP create/revoke/get tools calling the same service. MCP remains authenticated by the normal API token; `get_shared_run` accepts the share token separately as a tool argument. No token is written to application logs, traces, audit fields, tool result, or URL path/query.
- A dedicated bounded public projection containing only run name/status and group names with case counts, counts by result status, and summed known durations. Group names come from stored case section paths. Exclude comments, bug identifiers/details, user names, testcase titles/content/rich text, attachments, environment, milestones, custom fields, and internal IDs.
- Seven-day TTL. Unknown, expired, and revoked links return the same 404. No public list, search, or mutation endpoint.
- Public API and token-bearing management responses set `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, and `X-Robots-Tag: noindex`. The public Vue page also sets no-referrer/noindex metadata and loads no third-party assets.
- Management UI shows a disclosure and requires explicit confirmation before create. The link is shown once with copy action; it is not recoverable after leaving the screen. A separate `/shared-run` page reads the token from the URL fragment, removes the fragment immediately with `history.replaceState` before any request, then sends the token in an Authorization header using a client without the normal auth interceptor. It renders only the public projection and handles expiry/revoke as the same unavailable state.
- Update API maps, run lifecycle docs, access rules, deployment config documentation, and known errors.

## Out of scope

- Sharing bug details, testcase content, comments, identities, files, or mutation actions.
- Multiple simultaneously active links per run, long-lived snapshots, public list/search, query/path tokens, or logged-in user permission bypasses for management operations.
- Mobile layout/QA, as explicitly deferred by the user.

## Acceptance and checks

- Actor matrix: creator, active space owner, active same-company admin with membership, same-company admin without membership, ordinary collaborator, foreign-space actor, revoked space/company membership, and `created_by = NULL`.
- Link lifecycle: one-time token returned only at create; database contains no raw token; replacement revokes old link; explicit revoke and seven-day expiry both return the same 404; run deletion cascades link state.
- Public projection: allowlist assertion with comments, bugs, users, testcase rich text, attachments, custom fields, environment, and IDs seeded; none appear. Missing case snapshots render a bounded safe “Unassigned” group.
- Abuse and leakage: 30/min per token and 120/min per IP across processes; Redis unavailable fails closed; malformed/unknown tokens have generic responses; check application/MCP/proxy/access logs, traces, page URL/history/referrer, and browser network requests for token/payload leakage.
- REST and MCP create/revoke/get parity and safe response shape; MCP normal API authentication remains required.
- Headers and frontend: verify no-store/no-referrer/noindex on API responses and public document metadata; fragment removed before any network call; public page works even when a normal auth token is present and uses the share token only for redemption.
- Disposable DB only. Run Python compile, frontend ESLint/build, `git diff --check`, migration apply/replay, REST/MCP tests, concurrent rate/idempotency tests, and desktop browser checks. No real SMTP is involved.
- Keep the feature flags off until an independent security review and token-leakage matrix pass. Do not enable in production as part of this revision.

## Execution status — 2026-10-09

- **Implementation:** backend REST/MCP, v29 migration, Vue share dialog/public route, strict public-route app-shell bypass, privacy headers, default-off server/build flags, and required project documentation are implemented in the current working tree. Changes are pending the package commit.
- **Disposable runtime:** migration v29 was applied and replayed on `vtpad_su6_runtime_20261009`; schema has only the digest and version metadata, no raw token. Local disposable backend was restarted with the feature flag temporarily enabled for checks. Creator create/status/rotate/revoke/expiry, unauthenticated 401, non-member cross-space 404, REST/MCP projection equality, allowlist shape, and response privacy headers passed. Rate-limit 429 and Redis-failure 503 were separately verified. Temporary link rows and test-token files were removed.
- **Leakage evidence:** three minted test tokens were absent from the disposable backend runtime log. A desktop guest opened `/shared-run#<test-token>`; final browser URL had no fragment, page showed the generic unavailable state for the invalid token, and the backend recorded only `GET /api/v2/test-run/public/shared` for that guest. No user/profile/space requests were issued by the public route. A separate authenticated desktop route check confirmed the public shell does not redirect or mount navigation; the valid share projection was verified over REST and MCP service, not rendered in a browser.
- **External asset follow-up:** the production entry HTML previously injected Google Fonts before Vue could clear a share fragment. Replaced that loader with the already-installed local `roboto-fontface` files (regular/medium/bold) and removed the unused `unplugin-fonts` dependency. The rebuilt entry HTML and CSS contain no `fonts.googleapis.com` or `fonts.gstatic.com` references.
- **Code checks:** Python `compileall`, targeted frontend ESLint, Vite production build, production-entry font-reference scan, and `git diff --check` passed. Existing Sass legacy-API and large-chunk build warnings remain.
- **Independent review:** source review passed for authz/tenancy, token storage, public projection, rate-limit design, fragment handling, and FastMCP argument logging. Security acceptance remains **incomplete** because the actual external Traefik/access-log and trace-exporter configuration is outside this workspace, and a valid-token browser/network-history capture plus authenticated clipboard/keyboarding check has not been run. Keep production flags off until those checks are observed. After integrated checks, the disposable backend now reports `PUBLIC_RUN_LINKS_ENABLED=false`; the temporary second Vite server is stopped and the port-5173 dev server runs with `VITE_PUBLIC_RUN_LINKS_ENABLED=false`. The only backend restarted was `vtpad_disposable_ui_backend`, verified against database `vtpad_su6_runtime_20261009`; `vtpad_backend_app` was not restarted.

## File ownership

- Backend: `vtpad_backend/app/src/public_run/{__init__.py,dto.py,model.py,router.py,service.py}`, migration `v29_public_run_links.json`, config and app/MCP registration.
- Frontend: `testRunDetailComponent.vue`, a new public-run view component/page, and a dedicated public-run service/client. Avoid modifying the shared Axios interceptor.
- Docs: `project-docs/docs/api/{backend-modules-endpoints-index.md,service-endpoints-map.md}`, `project-docs/docs/flows/pad-run-lifecycle.md`, `project-docs/docs/rules/roles-and-access.md`, `project-docs/docs/ops/local-run-baseline.md`, `project-docs/docs/errors/common-errors.md`, backend `.env.example`.

## Rollback

Keep both feature flags off until acceptance passes. To roll back after enablement, disable the backend flag first, then frontend visibility; retain the table until operators confirm links are retired, then remove schema in a separate reviewed migration. The public redemption path must never bypass the backend flag during rollback.
