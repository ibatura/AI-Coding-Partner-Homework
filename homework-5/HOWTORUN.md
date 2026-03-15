# How to Run — Homework 5 Custom MCP Server

## Prerequisites

- Python 3.10+
- pip

---

## 1. Install Dependencies

```bash
cd homework-5/custom-mcp-server
pip install -r requirements.txt
```

This installs **fastmcp** and its dependencies.

---

## 2. Run the Server (standalone test)

```bash
python custom-mcp-server/server.py
```

The server starts and listens on stdio. You should see FastMCP startup output.

---

## 3. Connect MCP Configuration to Claude Code

Copy or symlink `.mcp.json` to your project root (already present in this folder).

Claude Code picks up `.mcp.json` automatically from the workspace root. Open the
homework-5 folder as your workspace:

```bash
claude  # inside homework-5/
```

Claude Code will detect `lorem-ipsum-server` and start it automatically.

Alternatively, register it globally via `claude mcp add`:

```bash
claude mcp add lorem-ipsum-server \
  --command python \
  --args custom-mcp-server/server.py
```

---

## 4. Use the `read` Tool

Once connected, ask Claude:

```
Use the read tool with word_count=50 to fetch lorem ipsum text.
```

Or call the resource directly:

```
Read the resource lorem://ipsum
```

Claude will invoke the tool/resource and return the requested number of words
from `lorem-ipsum.md`.

---

## 5. Verify the Tool Works (CLI test)

You can test the server without Claude using `fastmcp`:

```bash
cd homework-5
fastmcp dev custom-mcp-server/server.py
```

This opens the MCP inspector where you can manually call the `read` tool and
inspect the `lorem://ipsum` resource.

---

## Concepts

**Resources** are URIs that Claude can read from (e.g. files, APIs). They are
declared with `@mcp.resource` and fetched passively when Claude needs data.

**Tools** are actions Claude can invoke to perform operations (e.g. reading a
file, running a command). They are declared with `@mcp.tool` and called when
Claude decides to take an action.
