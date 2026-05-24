# MCP Setup Guide

VTPad acts as an MCP Server, exposing test management data to AI agents.

## What is MCP?

Model Context Protocol (MCP) is a standardized way for AI agents to interact with external data sources and tools. VTPad exposes its data as MCP tools, allowing agents to:

- Search and read test cases
- Create and update cases, suites, sections
- Manage test runs and results
- Search tech docs semantically
- Link bugs to test results

## Architecture

```
┌──────────────────────┐         MCP Protocol          ┌─────────────────────┐
│   AI Agent (Claude   │ ◄───── SSE / stdio ───────► │   VTPad Backend     │
│   Desktop, Cursor,   │        Authorization:         │   MCP Server        │
│   CLI tool)          │        Bearer <token>         │   /v1/mcp           │
└──────────────────────┘                                 └─────────────────────┘
```

**Important**: The AI agent runs locally. It reads your local code, Jira tickets, and files. VTPad only provides test data via MCP tools.

## Connecting Claude Desktop

### 1. Create an API Token

In VTPad web UI:
1. Go to your profile → API Tokens
2. Click "Create Token"
3. Copy the token (shown only once!)

Or via API:
```bash
curl -X POST http://localhost:8000/api/v2/api-token/ \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Claude Desktop"}'
```

### 2. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

```json
{
  "mcpServers": {
    "vtpad": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic-ai/mcp-proxy",
        "http://localhost:8000/v1/mcp"
      ],
      "env": {
        "API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

Or use SSE directly (if client supports it):
```json
{
  "mcpServers": {
    "vtpad": {
      "url": "http://localhost:8000/v1/mcp",
      "headers": {
        "Authorization": "Bearer your-api-token-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

After adding the config, restart Claude Desktop. You should see VTPad tools available.

## Available Tools (33 total)

### Discovery
| Tool | Description |
|------|-------------|
| `get_spaces` | List all accessible spaces |

### Test Cases
| Tool | Description |
|------|-------------|
| `get_case` | Get a single test case by ID |
| `search_cases` | Search test cases by query (title/text/steps) |
| `create_test_case` | Create a new test case |
| `update_test_case` | Update an existing test case |
| `delete_test_case` | Soft delete a test case |
| `hard_delete_test_case` | Permanently delete a test case |
| `find_similar_cases` | Find semantically similar cases |

### Test Suites
| Tool | Description |
|------|-------------|
| `get_suite` | Get suite with sections and cases |
| `create_suite` | Create a new test suite |
| `update_suite` | Update a test suite |
| `delete_suite` | Soft delete a suite |
| `hard_delete_suite` | Permanently delete a suite |

### Sections
| Tool | Description |
|------|-------------|
| `create_section` | Create a new section |
| `update_section` | Update a section |
| `delete_section` | Delete a section |
| `hard_delete_section` | Permanently delete a section |

### Test Runs & Results
| Tool | Description |
|------|-------------|
| `create_test_run` | Create a test run from suite or plan |
| `get_run_results` | Get all results for a run |
| `update_test_result` | Update a test result status/comment |
| `link_bug_to_result` | Link a bug to a test result |

### Tech Docs
| Tool | Description |
|------|-------------|
| `get_doc` | Get a tech doc by ID |
| `search_tech_docs` | Search tech docs |
| `create_tech_doc` | Create a tech doc |
| `update_tech_doc` | Update a tech doc |
| `delete_tech_doc` | Delete a tech doc |

### Semantic Search
| Tool | Description |
|------|-------------|
| `semantic_search_tech_docs` | Vector search in tech docs |
| `semantic_search_cases` | Vector search in test cases |

### Analytics
| Tool | Description |
|------|-------------|
| `get_analytics` | Get space analytics |
| `get_case_history` | Get run history for a case |

## Example Agent Workflows

### "Create test cases for user authentication"
```
1. Agent asks: "What space should I use?"
2. Agent calls get_spaces()
3. Agent searches tech docs for "authentication"
4. Agent creates test cases based on docs
```

### "Find tests related to password reset"
```
1. Agent calls semantic_search_cases("password reset")
2. Agent reviews found cases
3. Agent updates or creates missing cases
```

### "How did the login tests perform in the last run?"
```
1. Agent gets recent runs
2. Agent filters results for login-related cases
3. Agent summarizes pass/fail rates
```

## Troubleshooting

### Connection Refused
- Ensure backend is running: `uvicorn app.main:app --port 8000`
- Check firewall / port availability

### Authentication Failed
- Verify API token is correct (no extra spaces)
- Check token hasn't been deleted
- Token must be passed as `Authorization: Bearer <token>`

### Tools Not Showing
- Restart Claude Desktop after config changes
- Check Claude Desktop logs for errors
- Verify MCP proxy is installed: `npx @anthropic-ai/mcp-proxy --help`

## Security Notes

- API tokens are SHA256 hashed in the database
- Tokens can be revoked by deleting them
- MCP access is read-only by default; mutating tools require valid token
- JWT and API tokens use separate auth flows
