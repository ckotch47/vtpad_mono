# VTPad Backend

FastAPI-based backend for VTPad test management platform.

## Requirements

- Python 3.13+
- PostgreSQL 16+ (with pgvector extension)
- Redis
- Ollama (for embeddings, optional)

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
DB_NAME=vtpad
DB_USER=postgres
DB_PASSWORD=secret
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=your-secret-key
BACKEND_PORT=8000

# For embeddings (optional)
OLLAMA_HOST=http://localhost:11434
```

### 2. Database Setup

Enable pgvector extension:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python -c "
import asyncio
from app.migration import init, migration
asyncio.run(init())
asyncio.run(migration.run_migration())
"
```

### 5. Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

Or with the provided script:
```bash
bash scripts/start.sh
```

## Docker

```bash
docker-compose up --build
```

This starts PostgreSQL, Redis, and the backend app.

## Project Structure

```
app/
├── main.py                 # FastAPI app, router registration
├── migration.py            # Migration runner
├── src/
│   ├── common/             # Crypto, config, model scanner
│   ├── auth/               # JWT authentication
│   ├── users/              # User management
│   ├── spaces/             # Spaces (projects)
│   ├── test_suite/         # Test suites
│   ├── section/            # Sections (tree structure)
│   ├── test_case/          # Test cases + versions
│   ├── test_run/           # Test runs + results + step results
│   ├── test_plan/          # Test plans
│   ├── analytics/          # Dashboard analytics
│   ├── tech_doc/           # Tech documentation wiki
│   ├── embedding/          # Semantic search (pgvector)
│   ├── api_token/          # MCP API tokens
│   ├── bug/                # Legacy bug tracker
│   ├── comments/           # Bug comments
│   ├── tag/                # Tags
│   ├── notification/       # Notifications
│   ├── report/             # Reporting
│   ├── qa_report/          # QA reports
│   ├── environment/        # Test environments
│   ├── milestone/          # Milestones
│   ├── custom_field/       # Custom fields
│   ├── attachment/         # File attachments
│   └── mcp/                # MCP server (33 tools)
└── ...
```

## API Versions

- `/api/v1/` — Legacy endpoints (bugs, auth, spaces, reports)
- `/api/v2/` — New test management endpoints (suites, cases, runs, plans, analytics)
- `/v1/mcp` — MCP Server (SSE transport)

## Authentication

### JWT (Web)
```bash
POST /api/v1/auth/login
{ "email": "...", "password": "..." }
```

### API Token (MCP)
```bash
POST /api/v2/api-token/
{ "name": "My Token" }
```
Response includes `token` — save it, it's shown only once!

Use with MCP clients:
```
Authorization: Bearer <api-token>
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Development Notes

### Adding a New Module
1. Create folder under `app/src/{module}/`
2. Add `model.py`, `dto.py`, `service.py`, `router.py`, `__init__.py`
3. Import router in `app/main.py`
4. Add migration JSON if new tables

### Model Auto-Discovery
`common/models.py` scans all `model.py` files under `app/src/` automatically. No manual registration needed.

### Update Bug Fix
All update services filter `None` from `model_dump(exclude_unset=True)`:
```python
data = dto.model_dump(exclude_unset=True)
data = {k: v for k, v in data.items() if v is not None}
```
This prevents overwriting fields with NULL when not provided.
