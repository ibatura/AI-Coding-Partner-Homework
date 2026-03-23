# Task 4.2 — Custom FastMCP Server

## Overview
Build a custom MCP server using FastMCP that exposes pipeline results as queryable tools and resources. The server reads from `shared/results/` and makes data available to Claude Code.

---

## Step 1: Create the MCP Server File
**Action**: Create `mcp/server.py`
- Also create `mcp/__init__.py` (empty)

**Required dependency**: `fastmcp` (install via `pip install fastmcp`)

---

## Step 2: Implement Tool — `get_transaction_status`

### Specification
- **Name**: `get_transaction_status`
- **Input**: `transaction_id: str` (e.g., "TXN001")
- **Output**: JSON string with current status from `shared/results/`
- **Behavior**:
  1. Look for `{transaction_id}_result.json` or `{transaction_id}_rejected.json` in `shared/results/`
  2. If found: return the transaction data including status, settlement info, fraud score, etc.
  3. If not found: return `{"error": "Transaction not found", "transaction_id": "<id>"}`

### Implementation details:
- Use `pathlib.Path` to search `shared/results/`
- Parse the JSON file and return relevant fields
- Handle file-not-found gracefully
- Use `@mcp.tool()` decorator from FastMCP

---

## Step 3: Implement Tool — `list_pipeline_results`

### Specification
- **Name**: `list_pipeline_results`
- **Input**: None (no parameters)
- **Output**: JSON string with summary of all processed transactions
- **Behavior**:
  1. Read all JSON files in `shared/results/` (excluding `pipeline_summary.json`)
  2. For each: extract transaction_id, status, amount, currency, risk level
  3. Return a list of summaries
  4. Include aggregate counts: total, settled, rejected, held

### Implementation details:
- Use glob pattern `shared/results/TXN*.json` to find result files
- Parse each file and extract summary fields
- Return structured JSON
- Handle empty results directory gracefully (return empty list with counts = 0)

---

## Step 4: Implement Resource — `pipeline://summary`

### Specification
- **Name**: `pipeline://summary`
- **Type**: Resource (not a tool)
- **Output**: Plain text summary of the latest pipeline run
- **Behavior**:
  1. Read `shared/results/pipeline_summary.json` if it exists
  2. Format as human-readable text:
     ```
     Pipeline Run Summary
     ====================
     Run ID: <uuid>
     Completed: <timestamp>
     Total Transactions: 8
     Settled: 3
     Settled with Review: 2
     Held for Review: 1
     Rejected: 2
     Total Fees: $37.20
     Total Volume: $105,199.99
     ```
  3. If no summary file exists, return "No pipeline run found. Run the pipeline first."

### Implementation details:
- Use `@mcp.resource("pipeline://summary")` decorator from FastMCP
- Return text/plain content
- Format monetary values with comma separators and $ prefix

---

## Step 5: Server Setup and Entry Point

The server file should:
1. Import FastMCP: `from fastmcp import FastMCP`
2. Create server instance: `mcp = FastMCP("pipeline-status")`
3. Define the `shared/results/` path relative to project root
4. Register all tools and resources
5. Run with: `mcp.run()` at the bottom

### Full server structure:
```python
from fastmcp import FastMCP
import json
from pathlib import Path

mcp = FastMCP("pipeline-status")

RESULTS_DIR = Path(__file__).parent.parent / "shared" / "results"

@mcp.tool()
def get_transaction_status(transaction_id: str) -> str:
    """Get the current status of a transaction by ID."""
    # ... implementation

@mcp.tool()
def list_pipeline_results() -> str:
    """List a summary of all processed transactions."""
    # ... implementation

@mcp.resource("pipeline://summary")
def pipeline_summary() -> str:
    """Get the latest pipeline run summary."""
    # ... implementation

if __name__ == "__main__":
    mcp.run()
```

---

## Step 6: Verify the Server

Test that the server works:
1. Run the pipeline first (`python integrator.py`) so `shared/results/` has data
2. Start the MCP server: `python mcp/server.py`
3. In Claude Code, test:
   - Call `get_transaction_status` with "TXN001" — should return settled status
   - Call `get_transaction_status` with "TXN006" — should return rejected status
   - Call `list_pipeline_results` — should return 8 transaction summaries
   - Access `pipeline://summary` — should return formatted text

---

## Screenshot Requirement
- Capture a screenshot showing a custom MCP tool call (e.g., `get_transaction_status("TXN001")`)
- Combine with context7 screenshot into `docs/screenshots/mcp-interaction.png`

---

## Files to Create
- `mcp/__init__.py`
- `mcp/server.py`

## Dependencies
- `fastmcp` package (pip install)
- Task 2 completed (pipeline must have produced results in `shared/results/`)
- `mcp.json` configured (Task 4 parent)

## Notes
- The server must work with the standard `shared/results/` directory structure
- All file paths should be relative to the project root
- Handle edge cases: missing files, empty directories, malformed JSON
