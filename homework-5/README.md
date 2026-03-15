# Homework 5: Configure MCP Servers

**Author**: Ivan Batura

## Overview

This submission covers all four MCP tasks:

1. **GitHub MCP** — Connected Claude Code to GitHub via the official MCP server to list pull requests and summarize commits.
2. **Filesystem MCP** — Connected Claude to a local project directory; used it to list files and read source code.
3. **Jira MCP** — Connected Claude to Jira and queried the last 5 bug tickets from a project.
4. **Custom MCP Server** — Built a FastMCP server (`custom-mcp-server/`) exposing a `lorem://ipsum` resource and a `read` tool that returns a configurable number of words from a lorem ipsum file.

## Custom MCP Server — Key Design

| Concept | Implementation |
|---------|---------------|
| **Resource** | `lorem://ipsum` URI — Claude reads N words from `lorem-ipsum.md` passively |
| **Tool** | `read(word_count=30)` — Claude calls this to actively fetch word-limited content |

Resources are URIs that Claude can read from (e.g. files, APIs).
Tools are actions Claude can call to perform operations (e.g. reading a file, running a command).

## AI Tools Used

- Claude Code (claude-sonnet-4-6) for implementation and documentation
- FastMCP framework for the custom server

## Project Structure

```
homework-5/
├── README.md
├── HOWTORUN.md
├── TASKS.md
├── .mcp.json
├── custom-mcp-server/
│   ├── server.py
│   ├── lorem-ipsum.md
│   └── requirements.txt
└── docs/
    └── screenshots/
```

See [HOWTORUN.md](./HOWTORUN.md) for full setup and usage instructions.
