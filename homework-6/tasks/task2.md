# Task 2 — Agent 2: Build the Multi-Agent Pipeline

## Overview
Agent 2 is the **Code Generation Agent** — a **Claude sub-agent defined as a Markdown file**. When invoked, Claude reads this MD file's instructions and generates all the Python pipeline code (validator, fraud detector, settlement processor, integrator). The **agent itself is an MD file**; the **output is Python code**.

## Priority
⭐⭐⭐ Required — depends on Task 1 (specification).

## Important Distinction
| What | Format | Purpose |
|------|--------|---------|
| `agents/code_generation_agent.md` | Markdown (Claude sub-agent) | Instructions for Claude to generate all pipeline code |
| `agents/transaction_validator.py` | Python (output code) | Pipeline code produced BY the agent |
| `agents/fraud_detector.py` | Python (output code) | Pipeline code produced BY the agent |
| `agents/settlement_processor.py` | Python (output code) | Pipeline code produced BY the agent |
| `integrator.py` | Python (output code) | Pipeline orchestrator produced BY the agent |

## Tech Stack Decision (for the Python OUTPUT)
- **Language**: Python 3.10+
- **Decimal handling**: `decimal.Decimal` (stdlib)
- **JSON handling**: `json` (stdlib)
- **UUID generation**: `uuid.uuid4()` (stdlib)
- **Logging**: `logging` module (stdlib)
- **Testing**: `pytest` + `pytest-cov` (Task 5)

## MCP Requirement
During code generation, **use MCP context7** to look up Python libraries/patterns. Document at least 2 queries in `research-notes.md` (see subtask 2.5 and Task 4 for details).

---

## Step 1: Create the Code Generation Sub-Agent MD File

**Action**: Create `agents/code_generation_agent.md`

This is the **first file to create** — a Markdown file with Claude sub-agent instructions.

**The MD file must contain**:
- **Context section**: Reference `specification.md` (from Task 1), the `sample-transactions.json` data, the file-based messaging protocol, and the `shared/` directory structure
- **Task section**: Instruct Claude to generate all Python pipeline code: base agent class, 3 pipeline agents, and the integrator
- **Rules section**: Non-negotiable constraints — Decimal types, ISO 4217, audit logging, PII masking, JSON message envelopes, error handling
- **MCP instruction**: Remind Claude to use context7 to look up libraries during generation and log queries to `research-notes.md`
- **Output section**: List every file to create with its path and purpose

**Example structure**:
```markdown
# Code Generation Agent

## Context
Read `specification.md` for the full system specification.
Read `sample-transactions.json` to understand input data shape.
The pipeline uses file-based JSON message passing through shared/ directories.

## Task
Generate all pipeline code files:
1. `agents/base_agent.py` — shared base class with messaging utilities
2. `agents/transaction_validator.py` — validates fields, amounts, currencies
3. `agents/fraud_detector.py` — scores risk 0-10
4. `agents/settlement_processor.py` — calculates fees, settles/holds
5. `integrator.py` — orchestrates the full pipeline

## Rules
- Use decimal.Decimal for all monetary math (NEVER float)
- Validate currencies against ISO 4217 whitelist
- Mask account numbers in all log output
- Each agent must implement process_message(message: dict) -> dict
...

## MCP
Use context7 to look up Python decimal and logging libraries.
Document queries in research-notes.md.

## Output
Create all files listed above. Pipeline must be runnable via: python integrator.py
```

---

## Subtasks (Python code output)

These subtasks describe the **Python code that Agent 2 produces**:

| Subtask | File | Description |
|---------|------|-------------|
| 2.1 | `task2.1.md` | Transaction Validator agent (Python code) |
| 2.2 | `task2.2.md` | Fraud Detector agent (Python code) |
| 2.3 | `task2.3.md` | Settlement Processor agent (Python code) |
| 2.4 | `task2.4.md` | Integrator / Orchestrator (Python code) |
| 2.5 | `task2.5.md` | Research Notes (context7 queries) |

---

## Directory Structure to Create

```
project-root/
├── agents/
│   ├── code_generation_agent.md ← THE SUB-AGENT (MD file, created FIRST)
│   ├── __init__.py              ← Python package init (output)
│   ├── base_agent.py            ← shared base class (output)
│   ├── transaction_validator.py ← subtask 2.1 (output)
│   ├── fraud_detector.py        ← subtask 2.2 (output)
│   └── settlement_processor.py  ← subtask 2.3 (output)
├── shared/
│   ├── input/
│   ├── processing/
│   ├── output/
│   └── results/
├── integrator.py                ← subtask 2.4 (output)
├── sample-transactions.json     ← already exists
└── research-notes.md            ← subtask 2.5
```

---

## Shared Base Agent Design (Python output)

The code generation agent should instruct Claude to create `agents/base_agent.py` with:

1. **Abstract base class** `BaseAgent` with:
   - `__init__(self, name: str)` — sets agent name, configures logger
   - `process_message(self, message: dict) -> dict` — abstract method
   - `read_message(self, filepath: str) -> dict` — reads JSON from file
   - `write_message(self, message: dict, directory: str) -> str` — writes JSON to directory, returns filepath
   - `create_message_envelope(self, data: dict, target_agent: str, message_type: str) -> dict` — builds the standard message format with uuid, timestamp, source_agent, etc.
   - `mask_pii(self, text: str) -> str` — masks account numbers for logging
   - `setup_logging(self) -> logging.Logger` — configures audit trail logging

2. **Standard message format** (enforced by base class):
```json
{
  "message_id": "uuid4-string",
  "timestamp": "ISO-8601",
  "source_agent": "agent_name",
  "target_agent": "next_agent_name",
  "message_type": "transaction",
  "data": { ... }
}
```

---

## Execution Flow (what the Python output does)

```
sample-transactions.json
        │
        ▼
  ┌─────────────┐
  │  Integrator  │  ← Loads JSON, creates message envelopes, drops into shared/input/
  └──────┬──────┘
         │
         ▼
  ┌──────────────────────┐
  │ Transaction Validator │  ← Reads from shared/input/, validates, writes to shared/output/
  └──────────┬───────────┘
             │
             ▼
  ┌───────────────────┐
  │   Fraud Detector   │  ← Reads validated from shared/output/, scores risk, writes to shared/output/
  └─────────┬─────────┘
            │
            ▼
  ┌─────────────────────────┐
  │  Settlement Processor    │  ← Reads scored from shared/output/, settles, writes to shared/results/
  └─────────────────────────┘
```

- Rejected transactions at any stage go directly to `shared/results/` with status "rejected" and a reason field
- Each agent moves the file to `shared/processing/` while working on it

---

## Deliverables Checklist
- [ ] `agents/code_generation_agent.md` — the sub-agent MD file (created **FIRST**)
- [ ] `agents/__init__.py` (Python output)
- [ ] `agents/base_agent.py` (Python output)
- [ ] `agents/transaction_validator.py` (Python output, subtask 2.1)
- [ ] `agents/fraud_detector.py` (Python output, subtask 2.2)
- [ ] `agents/settlement_processor.py` (Python output, subtask 2.3)
- [ ] `integrator.py` (Python output, subtask 2.4)
- [ ] `research-notes.md` (subtask 2.5)
- [ ] `shared/` directory structure created by integrator on startup
- [ ] All 8 transactions from `sample-transactions.json` appear in `shared/results/`

## Dependencies
- Task 1 (`specification.md` and `agents/specification_agent.md` must exist)

## Feeds Into
- Task 3 (skills run the pipeline)
- Task 4 (MCP server queries results)
- Task 5 (tests cover each agent)
