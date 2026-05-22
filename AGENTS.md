# VTPad — Agent Guide

> VTPad is a full-stack QA/test-management web application. It is split into two independently deployable parts: a Python/FastAPI backend and a Vue 3/Vuetify frontend.

---

## Project Overview

| Part | Directory | Technology | Runtime |
|------|-----------|------------|---------|
| Backend | `vtpad_backend/` | Python 3.10, FastAPI, Tortoise ORM | Uvicorn inside Docker |
| Frontend | `vtpad_front_v2/` | Vue 3, Vuetify 3, Vite, Pinia | Node 20 inside Docker |

The backend exposes a REST API (prefixed with `/api` for the v1/v2 routers and also mounts legacy non-prefixed routers). It uses PostgreSQL as the primary database, Redis for caching/session storage, and Prometheus for metrics.

The frontend is a single-page application (SPA) served statically. It uses file-based routing (`src/pages/**/*.vue`) and feature-organized components.

Domain concepts you will see throughout the codebase:
- **Space** – a project/workspace.
- **Pad** – a test plan / collection item.
- **Run** – an execution of a pad.
- **Bug** – a defect/issue tracker item.
- **Testcase / Checklist** – structured test definitions.
- **Company / UserCompanySettings** – multi-tenancy and RBAC primitives.

---

## Repository Layout

```
vtpad_backend/
├── app/
│   ├── main.py              # FastAPI factory, CORS, Tortoise ORM registration
│   ├── imports.py           # Centralised module imports (mirrors main.py imports)
│   ├── migration.py         # Placeholder for data migrations
│   └── src/                 # Feature modules
│       ├── common/          # Config, crypto/JWT, models auto-discovery, guards
│       ├── admin/           # Company & user-company admin routers
│       ├── auth/            # Login, refresh tokens
│       ├── users/           # User CRUD, registration
│       ├── space/           # Spaces (projects)
│       ├── pad/             # Pads (test plans)
│       ├── padfolder/       # Folder organisation for pads
│       ├── run/             # Test runs
│       ├── runitems/        # Individual run items
│       ├── bug/             # Bug/issue tracking
│       ├── comments/        # Bug comments
│       ├── tag/             # Tags for bugs
│       ├── testcases/       # Test cases
│       ├── testcases_runitem/
│       ├── testcases_paditem/
│       ├── checklist/       # Checklists
│       ├── items/           # Generic items
│       ├── file/            # File uploads (stored in ./uploads)
│       ├── notes/           # Notes
│       ├── notification/    # In-app notifications
│       ├── news/            # News/announcements
│       ├── report/          # Reporting integration
│       ├── qa_report/       # QA-specific reports
│       ├── redis/           # Redis wrapper service
│       └── migration/data/  # Migration data helpers
│   └── utils/
│       ├── register_router.py  # Helper to batch-register APIRouters
│       └── jaeger.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml       # Production-like compose (Postgres + Redis + backend)
├── docker-compose.dev.yml   # Dev compose (+ Prometheus, Grafana, Jaeger)
└── uploads/                 # Uploaded files volume mount

vtpad_front_v2/
├── src/
│   ├── pages/               # File-based routes (unplugin-vue-router)
│   ├── layouts/             # Layout definitions
│   ├── components/          # Feature-based Vue SFCs
│   ├── stores/              # Pinia stores
│   ├── plugins/             # Vuetify, router, Pinia bootstrap
│   ├── router/              # Router instance (auto-routes + layouts)
│   └── styles/              # SCSS settings
├── package.json
├── vite.config.mjs
└── Dockerfile
```

---

## Technology Stack Details

### Backend
- **Framework:** FastAPI 0.111, Starlette
- **ORM:** Tortoise ORM 0.19.2 with `asyncpg` driver
- **Validation:** Pydantic v2
- **Auth:** JWT (`python-jose`), bcrypt hashing (`passlib`), OAuth2 password bearer
- **Caching / Sessions:** `aioredis` + custom wrapper in `app/src/redis/`
- **Mail:** `fastapi-mail` (optional, controlled by `use_mail` env var)
- **Observability:** Prometheus metrics via `prometheus-fastapi-instrumentator`; Jaeger/OpenTelemetry code exists but is mostly commented out
- **Concurrency:** Uvicorn with `uvloop` and `--workers 2` in production compose

### Frontend
- **Framework:** Vue 3.4, Vuetify 3.5
- **Build Tool:** Vite 5.1
- **State:** Pinia 2.1
- **Routing:** `vue-router` 4 with `unplugin-vue-router` (file-based) and `vite-plugin-vue-layouts`
- **HTTP Client:** Axios
- **Editor:** TipTap v2 (`@tiptap/vue-3` + extensions)
- **Charts:** `vue-chartjs` / Chart.js 4
- **Icons:** MDI font

### Infrastructure
- **Database:** PostgreSQL 14 (production compose) / 13.3 (dev compose)
- **Cache:** Redis 6
- **Reverse Proxy:** None bundled; backend runs behind `--proxy-headers` expecting an upstream proxy
- **CI/CD:** GitHub Actions (`.github/workflows/devdeploy.yml`) – deploys on merged PR to `dev` branch using a self-hosted runner

---

## Build & Run Commands

### Backend

```bash
cd vtpad_backend

# Local (requires Python 3.10, PostgreSQL, Redis)
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker (production-like)
docker-compose up -d --build

# Docker dev (includes Prometheus + Grafana + Jaeger)
docker-compose -f docker-compose.dev.yml up -d --build
```

### Frontend

```bash
cd vtpad_front_v2

# Install dependencies
npm install

# Development server (Vite HMR)
npm run dev          # listens on 0.0.0.0, port from Vite default (5173)

# Production build
npm run build

# Preview production build
npm run preview      # port 3000

# Production serve (inside Docker)
npm run prod         # serve -s dist -l 3000

# Docker
docker-compose up -d --build
```

### Lint

```bash
cd vtpad_front_v2
npm run lint         # ESLint with auto-fix
```

---

## Configuration & Environment Variables

Both parts rely on `.env` files. Examples are provided as `.env.example`.

### Backend (`vtpad_backend/.env`)

| Variable | Purpose |
|----------|---------|
| `db_name`, `db_user`, `db_password`, `db_host`, `db_port` | Primary PostgreSQL connection |
| `db_report_*` | Secondary PostgreSQL for reports |
| `backend_port` | Port exposed by docker-compose |
| `redis_host`, `redis_port`, `redis_user`, `redis_password` | Redis connection |
| `SECRET_KEY`, `ALGORITHM` | JWT signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token TTL |
| `report_url`, `report_port`, `report_api_hash` | External report-portal integration |
| `main_admin_id` | Super-admin user UUID |
| `use_mail` | Set to `1` to enable SMTP notifications |
| `MAIL_*` | SMTP settings (used only if `use_mail=1`) |
| `FRONTEND_URL`, `APP_NAME` | App metadata |

### Frontend (`vtpad_front_v2/.env`)

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE_URL` | Base URL for Axios API calls |
| `NODE_ENV` | Runtime environment flag |

---

## Code Organization Conventions

### Backend Module Pattern

Every feature module under `app/src/<feature>/` follows this structure:

```
<feature>/
├── __init__.py          # Usually exports router, models
├── model.py             # Tortoise ORM models
├── router.py            # FastAPI APIRouter (HTTP handlers)
├── service.py           # Business logic (static methods on *Service classes)
├── enum.py              # StrEnum / Enum definitions
├── dto/
│   └── *.py             # Pydantic request models (Create*Dto, Update*Dto, …)
└── rto/
    └── *.py             # Pydantic response models (Get*Rto, …)
```

Key conventions:
- Routers are instantiated as module-level variables (e.g. `router = APIRouter(prefix="/v1/bugs", ...)`).
- Services are typically classes with `@staticmethod` methods.
- Many services mix Tortoise ORM usage with **raw SQL** via `Tortoise.get_connection('default').execute_query_dict(...)` for complex joins.
- DTOs use Pydantic v2 models; some rely on `Depends()` for query-parameter binding.
- Global router registration happens in `app/main.py` via `app_utils.register_router([...], app, global_prefix='/api')` **and** via direct `app.include_router(...)` calls (legacy non-prefixed routes).

### Frontend Patterns

- **Routing:** File-based. Files in `src/pages/` become routes automatically. Dynamic segments use bracket notation, e.g. `[listId].vue`, `:spaceId/index.vue`.
- **Layouts:** Defined in `src/layouts/`. The default layout is `default.vue`. Layout assignment is handled by `vite-plugin-vue-layouts`.
- **Components:** Grouped by domain under `src/components/<domain>/`. Deep nesting is common (`bugs/modal/comment/...`).
- **State:** Pinia store in `src/stores/app.js` holds global UI state (opened bug, space ID, etc.).
- **API Calls:** Axios is used directly inside components/stores; there is no dedicated API client layer.
- **Auto-imports:** `unplugin-auto-import` handles `vue` and `vue-router` imports. Components are auto-imported by `unplugin-vue-components`.

---

## Authentication & Authorization

- The backend uses **JWT Bearer tokens**. `ACCESS_TOKEN_EXPIRE_MINUTES` is set very high (30000 min) in the example env; refresh tokens are stored in Redis.
- The `bearer` dependency (`OAuth2PasswordBearer`) is applied per-route with `Depends(bearer)`.
- A `user_payload(token)` helper decodes the JWT and raises `HTTPException(401)` on failure.
- Some endpoints additionally use `check_user_into_space` from `app/src/common/right_guard.py` for space-level authorization.
- Admin routes under `app/src/admin/` import role decorators (`roles_decorator.py`) and an `roles_enum.py`.

---

## Database & Migrations

- Tortoise ORM is configured in `app/main.py` with two connection pools: `default` (app data) and `report` (reporting data).
- Schema generation is disabled (`generate_schemas=False`); the project assumes the schema is managed externally or via the commented-out migration code in `lifespan`.
- `app/migration.py` and `app/src/migration/data/` contain ad-hoc migration helpers, but there is no formal migration framework (e.g. Aerich) configured.

---

## Testing

**There is currently no automated test suite.** No test runners, no test files, and no test scripts in `package.json` or CI. If you add tests:

- Backend: `pytest` + `httpx` + `tortoise.contrib.test` would be the natural fit.
- Frontend: `vitest` + `@vue/test-utils` would align with the Vite/Vue stack.

---

## Deployment

### Backend
The GitHub Actions workflow (`devdeploy.yml`) triggers on merged PRs to `dev`:
1. `git pull` on a self-hosted runner.
2. Overwrite `.env` from a repository variable (`DEV_ENV`).
3. `docker-compose up -d --build backend`.

### Frontend
The frontend Dockerfile:
1. Uses `node:20.10.0`.
2. Runs `npm ci`, installs `serve` globally, runs `npm run build`.
3. At runtime executes `npm run prod` (serves `dist/` on port 3000).

### Uploads
The backend mounts `./uploads` as a volume and serves it statically at `/uploads`.

---

## Security Considerations

- CORS is configured with `allow_origins=['*']` – permissive; tighten for production.
- JWT secret and algorithm come from environment variables. Do not commit `.env`.
- Passwords are hashed with bcrypt.
- Refresh tokens are stored in Redis and validated on refresh.
- There is **no rate-limiting middleware** in the current code.
- File uploads are saved to a local directory; ensure the host path is not writable by untrusted users.

---

## Notes for Agents

- The backend has a lot of commented-out instrumentation code (Jaeger, CProfile). Do not treat it as active.
- Raw SQL is prevalent in services; when modifying models, check for hard-coded table/column names in SQL strings.
- The project is a single monorepo with both parts under the same Git root. Backend and frontend changes can be committed atomically.
- The frontend `README.md` is the default Vuetify scaffolding readme and does not describe project-specific business logic.
- The backend `README.MD` is written in Russian and documents env variables in a free-form style.

## Documentation Policy

**Whenever you modify code, you MUST update the relevant documentation in `project-docs/docs/`.**

- Changing routes / DTOs / models → update `api/service-endpoints-map.md` and/or `api/backend-modules-endpoints-index.md`.
- Changing auth / flows / business logic → update the corresponding files in `flows/` or `architecture/`.
- Adding new external dependencies → update `integrations/dependencies.md`.
- Changing roles / permissions → update `rules/roles-and-access.md`.
- Fixing a known bug or limitation → update `errors/common-errors.md`.

Keep docs in sync with code. Do not leave documentation outdated after a change.
