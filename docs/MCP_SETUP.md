# MCP Server Setup for VTPad

VTPad exposes an MCP (Model Context Protocol) server at `/mcp`. Local AI agents (Claude Desktop, Cursor, Continue.dev, or custom CLI) can connect to it and manage test cases directly.

## Architecture

```
┌─────────────────────┐      SSE (HTTP)       ┌─────────────────────┐
│   Local AI Agent    │  ←──────────────────→  │   VTPad Backend     │
│  (Claude/Cursor)    │   Bearer <API_TOKEN>   │   /mcp endpoint     │
│                     │                        │                     │
│  - Project code     │                        │  - search_cases     │
│  - Jira tickets     │                        │  - create_case      │
│  - Local docs       │                        │  - get_suite_tree   │
└─────────────────────┘                        │  - create_run       │
                                               └─────────────────────┘
```

**Important:** AI runs locally. VTPad only provides data and tools. LLM inference happens on the user's machine.

---

## 1. Create an API Token

1. Open VTPad web UI
2. Go to **Settings → API Tokens**
3. Click **Create Token**
4. Name it (e.g., "Claude Desktop")
5. Copy the raw token (shown once)

---

## 2. Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "vtpad": {
      "url": "https://your-vtpad.com/mcp/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN_HERE"
      }
    }
  }
}
```

Restart Claude Desktop.

---

## 3. Cursor

Settings → MCP → Add Server:

| Field | Value |
|-------|-------|
| Name | vtpad |
| Type | SSE |
| URL | `https://your-vtpad.com/mcp/mcp` |
| Headers | `Authorization: Bearer YOUR_API_TOKEN_HERE` |

---

## 4. Custom Python Client

```python
from fastmcp import Client

async with Client("https://your-vtpad.com/mcp/mcp", headers={"Authorization": "Bearer YOUR_API_TOKEN"}) as client:
    tools = await client.list_tools()
    print([t.name for t in tools])
    
    result = await client.call_tool("search_test_cases", {
        "query": "OAuth2 authorization",
        "space_id": "your-space-id",
        "limit": 5
    })
    print(result.content[0].text)
```

---

## Available Tools

| Tool | Description |
|------|-------------|
| `search_test_cases` | Search cases by title/short_name in a space |
| `get_test_case` | Get full case details by ID |
| `get_suite_tree` | Get suite structure (sections + cases) |
| `get_space_suites` | List suites in a space |
| `create_test_case` | Create a new test case |

More tools coming: `create_test_run`, `get_run_results`, `update_test_result`, `search_tech_docs`.

---

## Security

- **API Token required** — JWT login tokens are NOT accepted
- Tokens can be revoked from VTPad UI
- Tokens have scopes (future: `mcp:read`, `mcp:write`)
- All tools respect space-level access
