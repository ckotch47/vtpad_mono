# VTPad API Reference

## Authentication

All endpoints require authentication via `Authorization: Bearer <token>` header.

- **Web**: JWT token from `/api/v1/auth/login`
- **MCP**: API token from `/api/v2/api-token/`

## Base URL

```
/api/v2/
```

---

## Test Suites

### List by Space
```
GET /test-suite/space/{space_id}
```
Query params: `page`, `page_size`, `sort_by`, `sort_order`, `search`

### Get by ID
```
GET /test-suite/{suite_id}
```

### Create
```
POST /test-suite/
```
Body: `{ name, description, space_id }`

### Update
```
PATCH /test-suite/{suite_id}
```
Body: `{ name?, description?, status? }`

### Delete
```
DELETE /test-suite/{suite_id}
```
Soft delete (sets status to deprecated).

### Update Sort
```
PATCH /test-suite/sort/{suite_id}
```
Body: `{ sort_before_id? | sort_after_id? }`

---

## Sections

### List by Suite
```
GET /section/suite/{suite_id}
```

### Get Tree
```
GET /section/suite/{suite_id}/tree
```
Returns nested tree with `children` and `test_case_count`.

### Get by ID
```
GET /section/{section_id}
```

### Create
```
POST /section/
```
Body: `{ name, description?, suite_id, parent_id? }`

### Update
```
PATCH /section/{section_id}
```
Body: `{ name?, description?, parent_id? }`

### Delete
```
DELETE /section/{section_id}
```
Hard delete. Cases become unassigned.

### Update Sort
```
PATCH /section/sort/{section_id}
```
Body: `{ sort_before_id? | sort_after_id? }`

---

## Test Cases

### List by Space
```
GET /test-case/space/{space_id}
```
Query params: `page`, `page_size`, `sort_by`, `sort_order`, `search`, `type`, `status`

### List by Suite
```
GET /test-case/suite/{suite_id}
```

### List by Section
```
GET /test-case/section/{section_id}
```

### Get by ID
```
GET /test-case/{testcase_id}
```
Includes `versions` array.

### Create
```
POST /test-case/
```
Body: `{ title, text?, steps?, expected_results?, preconditions?, postconditions?, type?, space_id, suite_id?, section_id?, short_name?, link?, external_id? }`

### Update
```
PATCH /test-case/{testcase_id}
```
Body: any fields. Creates version snapshot before update.

### Delete
```
DELETE /test-case/{testcase_id}
```
Soft delete (sets status to deprecated).

### Update Sort
```
PATCH /test-case/sort/{testcase_id}
```
Body: `{ sort_before_id? | sort_after_id? }`

### Duplicate
```
POST /test-case/{testcase_id}/duplicate
```
Creates a copy with "(Copy)" suffix in title.

### Run History
```
GET /test-case/{testcase_id}/runs
```
Query params: `page`, `page_size`
Returns all TestResult entries for this case across runs.

---

## Test Runs

### List by Space
```
GET /test-run/space/{space_id}
```
Query params: `page`, `page_size`, `sort_by`, `sort_order`, `search`

### Get by ID
```
GET /test-run/{run_id}
```

### Get with Results
```
GET /test-run/{run_id}/detail
```
Returns: `{ run, stats: {total, passed, failed, blocked, skipped, not_run}, results: [...] }`

### Create
```
POST /test-run/
```
Body: `{ name, description?, space_id, suite_id?, plan_id?, milestone_id?, environment_id?, testcase_ids? }`

If `plan_id` is provided, run uses plan's filtered case set.
If `suite_id` is provided directly, uses all cases from suite.
If `testcase_ids` provided, uses specific cases.

### Update
```
PATCH /test-run/{run_id}
```
Body: `{ name?, description?, status?, milestone_id?, environment_id? }`

### Start
```
POST /test-run/{run_id}/start
```
Transitions from `draft` → `active`.

### Complete
```
POST /test-run/{run_id}/complete
```
Transitions from `active` → `completed`.

### Delete
```
DELETE /test-run/{run_id}
```
Hard delete. Also deletes all results.

---

## Test Results

### Update Result
```
PATCH /test-run/result/{result_id}
```
Body: `{ status, duration_seconds?, comment?, linked_bug_ids? }`

### Bulk Update Results
```
PATCH /test-run/result/bulk
```
Body: `{ result_ids: [...], status }`

### Get Step Results
```
GET /test-run/result/{result_id}/steps
```
Returns array of step-level results.

### Update Step Results
```
PATCH /test-run/result/{result_id}/steps
```
Body: `{ steps: [{ step_index, step_text?, status, comment?, screenshot_url? }] }`

---

## Test Plans

### List by Space
```
GET /test-plan/space/{space_id}
```
Query params: `page`, `page_size`, `sort_by`, `sort_order`, `search`

### Get by ID
```
GET /test-plan/{plan_id}
```

### Get Filtered Cases
```
GET /test-plan/{plan_id}/cases
```
Returns cases matching plan's filters.

### Create
```
POST /test-plan/
```
Body: `{ name, description?, space_id, suite_id?, filters? }`

### Update
```
PATCH /test-plan/{plan_id}
```
Body: `{ name?, description?, suite_id?, filters? }`

### Delete
```
DELETE /test-plan/{plan_id}
```

---

## Analytics

### Space Stats
```
GET /analytics/space/{space_id}
```
Returns: `{ cases: {total, manual, checklist, automated}, suites, runs: {total, active}, latest_results: {...} }`

### Run Trend
```
GET /analytics/space/{space_id}/trend?days=30
```
Returns daily pass/fail counts for completed runs.

### Top Failed Cases
```
GET /analytics/space/{space_id}/top-failed?limit=10
```
Returns cases with most failures.

### Suite Coverage
```
GET /analytics/suite/{suite_id}/coverage
```
Returns: `{ total, manual, checklist, automated, percentages: {...} }`

---

## Tech Docs

### List by Space
```
GET /tech-doc/space/{space_id}
```
Query params: `page`, `page_size`, `search`

### Get Tree
```
GET /tech-doc/space/{space_id}/tree
```

### Get by ID
```
GET /tech-doc/{doc_id}
```

### Create
```
POST /tech-doc/
```
Body: `{ space_id, title, content?, doc_type?, parent_id? }`

### Update
```
PATCH /tech-doc/{doc_id}
```
Body: `{ title?, content?, doc_type?, parent_id? }`

### Delete
```
DELETE /tech-doc/{doc_id}
```

---

## API Tokens

### List
```
GET /api-token/
```

### Create
```
POST /api-token/
```
Body: `{ name }`
Returns: `{ id, name, token, created_at }` — token shown only once!

### Delete
```
DELETE /api-token/{token_id}
```

---

## Legacy v1 Endpoints

Bugs, spaces, users, auth, notifications, reports use `/api/v1/` prefix.
See backend code for details.
