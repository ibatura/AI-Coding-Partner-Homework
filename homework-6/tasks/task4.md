# Task 4 — MCP Integration

## Overview
Integrate **two** MCP servers: (1) **context7** for library lookups during code generation, and (2) a **custom FastMCP server** that makes the pipeline queryable. Both must be configured in a single `mcp.json`.

## Priority
⭐⭐ Required — context7 usage happens during Task 2; custom MCP server depends on Task 2 output.

## Subtasks

| Subtask | File | Description |
|---------|------|-------------|
| 4.1 | `task4.1.md` | context7 Integration |
| 4.2 | `task4.2.md` | Custom FastMCP Server |

---

## Combined `mcp.json`

**Action**: Create `mcp.json` in the project root with both servers:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "pipeline-status": {
      "command": "python",
      "args": ["mcp/server.py"]
    }
  }
}
```

---

## Directory Structure

```
project-root/
├── mcp/
│   ├── __init__.py
│   └── server.py           ← custom FastMCP server (subtask 4.2)
├── mcp.json                 ← combined config
├── research-notes.md        ← context7 queries (subtask 4.1 / also subtask 2.5)
└── docs/
    └── screenshots/
        └── mcp-interaction.png  ← screenshot of context7 + custom MCP calls
```

---

## Deliverables Checklist
- [ ] `mcp.json` — both context7 and pipeline-status configured
- [ ] `mcp/server.py` — custom FastMCP server (subtask 4.2)
- [ ] `research-notes.md` — at least 2 context7 queries documented (shared with subtask 2.5)
- [ ] `docs/screenshots/mcp-interaction.png` — screenshot of context7 query AND custom MCP tool call

## Dependencies
- Task 2 (`shared/results/` must have data for MCP server to query)
- Node.js/npx available for context7

## Feeds Into
- Task 5 (tests can cover MCP server)
