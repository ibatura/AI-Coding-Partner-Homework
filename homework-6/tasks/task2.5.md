# Task 2.5 — Research Notes (context7 Queries)

## Overview
Document at least 2 context7 MCP queries made during pipeline development. This file serves as evidence of MCP usage during code generation (Agent 2 — the code generation sub-agent).

## Step 1: Configure context7 in `mcp.json`

Ensure `mcp.json` includes the context7 server (also covered in Task 4):
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

---

## Step 2: Perform and Document Queries

Create `research-notes.md` in the project root with at least 2 queries.

These queries should happen while the **Code Generation sub-agent** (`agents/code_generation_agent.md`) is being used to generate the pipeline code.

### Suggested Query 1: Decimal / Monetary Arithmetic
- **Search**: "Python decimal module" or "decimal.Decimal precision rounding"
- **Why**: Need to understand `ROUND_HALF_UP`, quantize, and best practices for monetary calculations
- **Document**: The context7 library ID returned, and the key insight applied (e.g., use `Decimal("0.001")` string constructor, never `Decimal(0.001)` float constructor)

### Suggested Query 2: Python Logging / Structured Logging
- **Search**: "Python logging module structured logging" or "Python logging JSON format"
- **Why**: Need audit trail logging with consistent format across all agents
- **Document**: The context7 library ID returned, and the pattern applied (e.g., custom formatter, log record fields)

### Alternative Queries (pick any if above don't work):
- "Python pathlib file operations" — for file-based messaging
- "Python uuid module" — for message_id generation
- "Python datetime ISO 8601" — for timestamp handling
- "FastMCP Python server" — for Task 4 MCP server

---

## Step 3: Format Each Entry

Each entry in `research-notes.md` must follow this format:
```markdown
## Query N: [Topic]
- **Search**: [What you searched for]
- **context7 library ID**: [The ID context7 returned]
- **Key insight**: [What you learned]
- **Applied in**: [Which file/function this was applied to]
```

---

## Files to Create
- `research-notes.md`

## Dependencies
- `mcp.json` with context7 configured (Task 4)
- Queries happen while using `agents/code_generation_agent.md` to generate code

## Feeds Into
- Task 4 deliverables (research-notes.md is a Task 4 deliverable too)
