# AI Integration Architecture for VTPad

## Overview

VTPad выступает **MCP Server** — стандартизированный источник контекста и инструментов для локальных AI-агентов тестировщиков.

**AI-агент работает локально** у тестера (Claude Desktop, Cursor, Continue.dev, или кастомный CLI). У агента есть полный контекст проекта (код, задача, требования). Агент сам ходит на VTPad через MCP, получает тестовые данные, создаёт/обновляет кейсы и возвращает результат пользователю.

**VTPad не содержит ИИ.** VTPad — это backend с:
1. **MCP Server** — набор tools и resources для агентов
2. **RAG** — векторный поиск по тестам и tech docs
3. **Tech Docs** — документация тестируемого проекта

---

## 1. Архитектура взаимодействия

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ЛОКАЛЬНАЯ МАШИНА ТЕСТЕРА                          │
│  ┌──────────────────────┐                                                   │
│  │   AI Агент (MCP      │  MCP Client (Claude Desktop / Cursor / CLI)       │
│  │   Client)            │                                                   │
│  │                      │  Контекст (локальный, НЕ ходит на сервер):        │
│  │  • код проекта       │  - исходный код (читает локально)                 │
│  │  • задача из Jira    │  - задача / тикет (подключение к Jira/etc)        │
│  │  • локальные docs    │  - README, API docs, требования (локальные файлы) │
│  │  • IDE / терминал    │  - diff / branch / PR                             │
│  └──────────┬───────────┘                                                   │
│             │ MCP Protocol (SSE / stdio)                                    │
│             │ Authorization: Bearer <API_TOKEN>                             │
└─────────────┼───────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VTPAD BACKEND (MCP Server)                          │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   MCP Tools     │  │   MCP Resources │  │        RAG Engine           │  │
│  │                 │  │                 │  │                             │  │
│  │ search_cases    │  │ tech_docs/*     │  │  pgvector (PostgreSQL)      │  │
│  │ create_case     │  │ suites/*        │  │  embeddings table           │  │
│  │ update_case     │  │ cases/*         │  │  semantic search            │  │
│  │ get_suite_tree  │  │ runs/*          │  │  hybrid search (tsvector)   │  │
│  │ create_run      │  │ checklists/*    │  │                             │  │
│  │ update_result   │  │                 │  │  Test cases                 │  │
│  │ search_tech_docs│  │                 │  │  Tech docs                  │  │
│  │ link_bug        │  │                 │  │  Suites / Sections          │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
│                                                                             │
│  FastAPI Application                                                        │
│  - MCP SSE endpoint: /mcp/sse                                               │
│  - MCP messages: /mcp/messages                                              │
│  - Standard REST API: /api/v1/* (для фронтенда)                             │
│  - Auth: JWT/API Token (одинаковая система для REST и MCP)                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Поток работы

1. **Тестер запускает локальный агент** (уже настроенный с MCP server URL и API токеном)
2. **Агент подключается к VTPad по MCP** (SSE transport)
3. **Тестер пишет агенту**: "Найди существующие тесты авторизации и создай новый для OAuth2"
4. **Агент (локально)**:
   - Читает локальный код проекта (OAuth2 implementation)
   - Вызывает `search_cases(query="OAuth2 authorization")` → получает существующие кейсы из VTPad
   - Вызывает `search_tech_docs(query="OAuth2 flow")` → получает документацию
   - Генерирует новый тест-кейс (LLM inference локально или через API)
   - Вызывает `create_case(...)` → сохраняет в VTPad
   - Показывает пользователю результат + ссылку на созданный кейс

---

## 2. MCP Server в FastAPI

### Transport: SSE (Server-Sent Events)

```python
# FastAPI endpoints для MCP

@mcp_app.get("/mcp/sse")
async def mcp_sse(request: Request):
    """SSE endpoint — агент подключается сюда и слушает events."""
    # Проверяем API Token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_api_token(token)
    
    # Создаём MCP session
    session = MCPSession(user=user)
    return EventSourceResponse(session.event_generator())

@mcp_app.post("/mcp/messages")
async def mcp_messages(request: Request):
    """Агент POST-ит сюда JSON-RPC messages."""
    body = await request.json()
    return await handle_mcp_message(body)
```

### Альтернатива: stdio transport
Если тестер хочет запускать MCP server локально как subprocess:
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "vtpad": {
      "command": "python",
      "args": ["-m", "vtpad_mcp_server", "--token", "<API_TOKEN>"],
      "env": {"VTPAD_URL": "https://vtpad.company.com"}
    }
  }
}
```
Но SSE проще — один центральный сервер, агенты просто подключаются.

### MCP Tools — полный список

#### `search_test_cases`
Семантический + текстовый поиск по кейсам.
```json
{
  "name": "search_test_cases",
  "description": "Search test cases by semantic similarity or text match",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Search query (natural language)"},
      "suite_id": {"type": "string", "description": "Filter by suite UUID"},
      "section_id": {"type": "string", "description": "Filter by section UUID"},
      "status": {"type": "string", "enum": ["draft", "active", "deprecated"]},
      "type": {"type": "string", "enum": ["manual", "automated", "checklist"]},
      "limit": {"type": "integer", "default": 10},
      "use_semantic": {"type": "boolean", "default": true}
    },
    "required": ["query"]
  }
}
```

#### `find_similar_cases`
Найти кейсы семантически похожие на данный.
```json
{
  "name": "find_similar_cases",
  "inputSchema": {
    "type": "object",
    "properties": {
      "case_id": {"type": "string"},
      "limit": {"type": "integer", "default": 5}
    },
    "required": ["case_id"]
  }
}
```

#### `get_case_details`
Полная информация о кейсе.
```json
{
  "name": "get_case_details",
  "inputSchema": {
    "type": "object",
    "properties": {
      "case_id": {"type": "string"}
    },
    "required": ["case_id"]
  }
}
```

#### `get_case_history`
История запусков кейса.
```json
{
  "name": "get_case_history",
  "inputSchema": {
    "type": "object",
    "properties": {
      "case_id": {"type": "string"},
      "limit": {"type": "integer", "default": 20}
    },
    "required": ["case_id"]
  }
}
```

#### `get_suite_tree`
Полная структура suite → sections → cases.
```json
{
  "name": "get_suite_tree",
  "inputSchema": {
    "type": "object",
    "properties": {
      "suite_id": {"type": "string"}
    },
    "required": ["suite_id"]
  }
}
```

#### `create_test_case`
```json
{
  "name": "create_test_case",
  "description": "Create a new test case. Returns the created case ID.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "suite_id": {"type": "string", "description": "Suite UUID"},
      "section_id": {"type": ["string", "null"], "description": "Section UUID or null"},
      "title": {"type": "string"},
      "type": {"type": "string", "enum": ["manual", "automated", "checklist"], "default": "manual"},
      "description": {"type": "string"},
      "preconditions": {"type": "string"},
      "steps": {"type": "string"},
      "expected_results": {"type": "string"},
      "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["suite_id", "title", "type"]
  }
}
```

#### `update_test_case`
```json
{
  "name": "update_test_case",
  "description": "Update an existing test case. Only provided fields are updated.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "case_id": {"type": "string"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "preconditions": {"type": "string"},
      "steps": {"type": "string"},
      "expected_results": {"type": "string"},
      "status": {"type": "string", "enum": ["draft", "active", "deprecated"]}
    },
    "required": ["case_id"]
  }
}
```

#### `create_test_run`
```json
{
  "name": "create_test_run",
  "inputSchema": {
    "type": "object",
    "properties": {
      "suite_id": {"type": "string"},
      "name": {"type": "string"},
      "environment": {"type": "string", "description": "e.g. staging, production"},
      "milestone": {"type": "string"},
      "filter": {"type": "object", "description": "Optional filters: sections, types, tags"}
    },
    "required": ["suite_id", "name"]
  }
}
```

#### `get_run_results`
```json
{
  "name": "get_run_results",
  "inputSchema": {
    "type": "object",
    "properties": {
      "run_id": {"type": "string"},
      "status": {"type": "string", "enum": ["passed", "failed", "skipped", "blocked", "not_run"]}
    },
    "required": ["run_id"]
  }
}
```

#### `update_test_result`
```json
{
  "name": "update_test_result",
  "description": "Update test result status and comment",
  "inputSchema": {
    "type": "object",
    "properties": {
      "result_id": {"type": "string"},
      "status": {"type": "string", "enum": ["passed", "failed", "skipped", "blocked", "not_run"]},
      "comment": {"type": "string"},
      "duration_seconds": {"type": "number"},
      "linked_bug_ids": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["result_id", "status"]
  }
}
```

#### `link_bug_to_result`
```json
{
  "name": "link_bug_to_result",
  "inputSchema": {
    "type": "object",
    "properties": {
      "result_id": {"type": "string"},
      "bug_short_name": {"type": "string", "description": "e.g. PROJ-123"}
    },
    "required": ["result_id", "bug_short_name"]
  }
}
```

#### `search_tech_docs`
Поиск по документации тестируемого проекта.
```json
{
  "name": "search_tech_docs",
  "description": "Search technical documentation of the project under test",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "doc_type": {"type": "string", "enum": ["api_doc", "prd", "manual", "wiki", "migration", "other"]},
      "limit": {"type": "integer", "default": 5}
    },
    "required": ["query"]
  }
}
```

#### `get_tech_doc`
```json
{
  "name": "get_tech_doc",
  "inputSchema": {
    "type": "object",
    "properties": {
      "doc_id": {"type": "string"}
    },
    "required": ["doc_id"]
  }
}
```

#### `create_suite`
```json
{
  "name": "create_suite",
  "inputSchema": {
    "type": "object",
    "properties": {
      "space_id": {"type": "string"},
      "name": {"type": "string"},
      "description": {"type": "string"}
    },
    "required": ["space_id", "name"]
  }
}
```

#### `create_section`
```json
{
  "name": "create_section",
  "inputSchema": {
    "type": "object",
    "properties": {
      "suite_id": {"type": "string"},
      "parent_id": {"type": ["string", "null"]},
      "name": {"type": "string"}
    },
    "required": ["suite_id", "name"]
  }
}
```

#### `get_space_suites`
Список suites в space.
```json
{
  "name": "get_space_suites",
  "inputSchema": {
    "type": "object",
    "properties": {
      "space_id": {"type": "string"}
    },
    "required": ["space_id"]
  }
}
```

#### `get_analytics`
Статистика.
```json
{
  "name": "get_analytics",
  "inputSchema": {
    "type": "object",
    "properties": {
      "space_id": {"type": "string"},
      "metric": {"type": "string", "enum": ["failure_rate", "coverage", "run_count", "suite_stats"]}
    },
    "required": ["space_id", "metric"]
  }
}
```

### MCP Resources (URI-based access)

Агент может читать ресурсы по URI без tool call:

| URI | Описание |
|-----|----------|
| `tech-docs://{doc_id}` | Полный текст tech doc |
| `case://{case_id}` | Полный текст test case |
| `suite://{suite_id}/tree` | Дерево suite |
| `run://{run_id}/results` | Результаты run |
| `space://{space_id}/suites` | Список suites |

---

## 3. RAG — Векторный поиск

### pgvector
```sql
-- Расширение
CREATE EXTENSION IF NOT EXISTS vector;

-- Таблица embeddings
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    space_id UUID NOT NULL,
    source_type VARCHAR(50) NOT NULL,  -- 'test_case', 'suite', 'section', 'tech_doc'
    source_id UUID NOT NULL,
    source_field VARCHAR(50),          -- 'title', 'description', 'steps', 'full_text'
    text_chunk TEXT NOT NULL,
    embedding VECTOR(1536),            -- OpenAI text-embedding-3-small
    created_at TIMESTAMP DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_embeddings_space_type ON embeddings (space_id, source_type);
CREATE INDEX idx_embeddings_source ON embeddings (source_type, source_id);
```

### Embedding pipeline
```
При CREATE / UPDATE TestCase / TechDoc / Suite / Section:
  1. strip HTML → plain text
  2. chunk (test_case целиком, tech_doc по 1000 tokens)
  3. generate embedding (async, через embedding API)
  4. DELETE FROM embeddings WHERE source_type=X AND source_id=Y
  5. INSERT INTO embeddings ...
```

### Semantic search
```python
async def semantic_search(
    space_id: str,
    query: str,
    source_types: list[str] | None = None,
    top_k: int = 10,
    min_score: float = 0.7
) -> list[dict]:
    query_embedding = await embed_text(query)  # OpenAI or local
    results = await db.fetch(
        """
        SELECT source_type, source_id, source_field, text_chunk,
               1 - (embedding <=> :q) AS score
        FROM embeddings
        WHERE space_id = :space_id
          AND (:types IS NULL OR source_type = ANY(:types))
          AND 1 - (embedding <=> :q) > :min_score
        ORDER BY embedding <=> :q
        LIMIT :top_k
        """,
        {"q": query_embedding, "space_id": space_id, "types": source_types, "min_score": min_score, "top_k": top_k}
    )
    return results
```

### Гибридный поиск
```python
async def hybrid_search(space_id, query, limit=10):
    # Semantic
    semantic_results = await semantic_search(space_id, query, limit=limit * 2)
    # Full-text (PostgreSQL tsvector)
    text_results = await fulltext_search(space_id, query, limit=limit * 2)
    # Reciprocal Rank Fusion
    return rrf_merge(semantic_results, text_results, k=60)[:limit]
```

---

## 4. Tech Docs — Документация тестируемого проекта

### Модель
```python
class TechDocModel:
    id: UUID
    space_id: UUID
    title: str
    content: str                    # HTML / Markdown / plain text
    source_url: str | None          # откуда импортировано
    doc_type: str                   # api_doc, prd, manual, wiki, migration, other
    version: str | None
    content_hash: str               # sha256 для дедупликации
    created_at: datetime
    updated_at: datetime
```

### API (REST — для фронтенда импорта)
- `POST /api/v1/tech-docs` — создать
- `GET /api/v1/tech-docs?space_id=&doc_type=` — список
- `GET /api/v1/tech-docs/{id}` — прочитать
- `PUT /api/v1/tech-docs/{id}` — обновить
- `DELETE /api/v1/tech-docs/{id}` — удалить
- `POST /api/v1/tech-docs/{id}/reindex` — пересоздать embeddings

### Импорт (UI)
1. Paste Markdown/HTML в textarea
2. Upload .md / .html файл
3. Confluence URL + API key
4. Swagger/OpenAPI URL → парсинг эндпоинтов
5. Notion page URL + integration token

---

## 5. Auth & Security

### API Token
Тот же JWT токен, что и для REST API. MCP SSE endpoint проверяет `Authorization: Bearer <token>`.

```python
async def verify_mcp_auth(request: Request) -> User:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return await jwt_verify(token)
```

### Права доступа
- Все MCP tools фильтруют по `space_id` — пользователь видит только свои spaces
- `search_test_cases` → только cases из spaces пользователя
- `create_case` → проверка прав на suite
- `search_tech_docs` → только docs из доступных spaces

### Rate limiting
- MCP endpoints: 60 requests/min на пользователя
- Embedding generation: 100 docs/min

---

## 6. Implementation Plan

### Phase 1: MCP Server Skeleton (3-4 дня)
- [ ] Добавить `mcp` Python SDK зависимость
- [ ] Создать `app/src/mcp/` модуль
- [ ] SSE transport endpoint `/mcp/sse`
- [ ] JSON-RPC message handler `/mcp/messages`
- [ ] Tool registration framework
- [ ] 3 core tools: `search_test_cases`, `get_case_details`, `get_suite_tree`

### Phase 2: RAG + pgvector (3-4 дня)
- [ ] Установить pgvector расширение
- [ ] Миграция `embeddings` таблицы
- [ ] `EmbeddingService` (генерация + поиск)
- [ ] Auto-index при create/update TestCase / TechDoc
- [ ] Semantic search endpoint (для MCP tool)

### Phase 3: Tech Docs (2-3 дня)
- [ ] Модель `TechDocModel` + CRUD endpoints
- [ ] Импорт UI (paste + upload)
- [ ] Embedding для tech docs
- [ ] MCP tools: `search_tech_docs`, `get_tech_doc`

### Phase 4: Full MCP Tools (3-4 дня)
- [ ] `create_test_case`, `update_test_case`
- [ ] `create_test_run`, `get_run_results`, `update_test_result`
- [ ] `link_bug_to_result`
- [ ] `create_suite`, `create_section`, `get_space_suites`
- [ ] `get_case_history`, `get_analytics`

### Phase 5: Client Examples (2-3 дня)
- [ ] `mcp.json` конфиг для Claude Desktop
- [ ] README для подключения Cursor / Continue.dev
- [ ] Пример CLI-агента на Python

---

## 7. Client Setup Examples

### Claude Desktop
```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "vtpad": {
      "url": "https://vtpad.company.com/mcp/sse",
      "headers": {
        "Authorization": "Bearer ${VTPAD_API_TOKEN}"
      }
    }
  }
}
```

### Cursor
Settings → MCP → Add Server:
```
Name: vtpad
URL: https://vtpad.company.com/mcp/sse
Headers: Authorization: Bearer <token>
```

### Environment Variable
```bash
export VTPAD_API_TOKEN="eyJhbGciOiJIUzI1NiIs..."
export VTPAD_URL="https://vtpad.company.com"
```

---

## 8. Стоимость

| Компонент | Стоимость | Примечание |
|-----------|-----------|------------|
| Embeddings (OpenAI) | $0.02 / 1M tokens | ~$0.01 за индексацию space |
| LLM inference | Локально или пользовательский API key | Агент использует СВОЙ ключ |
| pgvector | Бесплатно | Часть PostgreSQL |
| MCP Server | Бесплатно | FastAPI endpoint |

**VTPad backend НЕ платит за LLM inference.** LLM работает локально у тестера (Claude Desktop, Cursor, Ollama и т.д.). VTPad только предоставляет данные и embeddings.
