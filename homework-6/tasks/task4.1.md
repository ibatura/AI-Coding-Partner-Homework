# Task 4.1 — context7 MCP Integration

## Overview
Configure and use the context7 MCP server during code generation to look up Python libraries and patterns. Document at least 2 queries in `research-notes.md`.

---

## Step 1: Ensure context7 is in `mcp.json`

Verify `mcp.json` includes:
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

**Prerequisite**: `npx` must be available (Node.js installed).

---

## Step 2: Perform context7 Queries During Development

Use context7 while implementing the pipeline agents (Task 2). The queries should be genuine — look up real library documentation.

### Recommended Query 1: Python `decimal` module
- **When**: While implementing amount validation (subtask 2.1) and fee calculation (subtask 2.3)
- **What to search**: "Python decimal module" or "decimal.Decimal"
- **What to learn**: `ROUND_HALF_UP` rounding mode, `quantize()` for fixed precision, string constructor vs float constructor
- **Apply**: In `agents/transaction_validator.py` and `agents/settlement_processor.py`

### Recommended Query 2: Python `logging` or `pathlib`
- **When**: While implementing base agent (subtask 2.1) or integrator (subtask 2.4)
- **What to search**: "Python logging structured" or "Python pathlib"
- **What to learn**: Custom formatters, log levels, or Path operations for file-based messaging
- **Apply**: In `agents/base_agent.py` or `integrator.py`

### Alternative queries:
- "FastMCP Python" — for building the custom MCP server (subtask 4.2)
- "pytest fixtures" — for test setup (Task 5)
- "Python json module" — for message serialization

---

## Step 3: Document in `research-notes.md`

For each query, document:
```markdown
## Query N: [Topic]
- **Search**: [Exact search string used]
- **context7 library ID**: [The ID returned by context7]
- **Key insight**: [What you learned that was new or useful]
- **Applied in**: [File and function where this was used]
```

Minimum: 2 queries. More is better for demonstrating genuine MCP usage.

---

## Screenshot Requirement
- Capture a screenshot showing a context7 query and its response
- This will be combined with the custom MCP screenshot into `docs/screenshots/mcp-interaction.png`

---

## Files to Create/Update
- `research-notes.md` (create or update — shared with subtask 2.5)

## Dependencies
- Node.js/npx installed
- `mcp.json` configured

## Notes
- context7 queries should happen **during** code generation, not after the fact
- The queries should be genuine lookups, not fabricated entries
