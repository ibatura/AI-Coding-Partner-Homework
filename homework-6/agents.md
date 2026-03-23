# Agents — AI-Powered Multi-Agent Banking Pipeline

This document defines the four **meta-agents** (Claude sub-agents) that build the banking transaction processing system, and the three **pipeline agents** they produce.

---

## Meta-Agents (Claude Sub-Agents)

These are Markdown files that instruct Claude to generate outputs. They are NOT Python scripts.

---

### Agent 1 — Specification Agent

| Field | Value |
|-------|-------|
| **File** | `agents/specification_agent.md` |
| **Role** | Generates the complete technical specification for the pipeline |
| **Reads** | `sample-transactions.json`, `specification-TEMPLATE-hint.md` |
| **Produces** | `specification.md` with all 5 sections |
| **Dependencies** | None (runs first) |
| **Triggered by** | `/write-spec` slash command (`.claude/commands/write-spec.md`) |

**Project context**: The agent analyses 8 sample transactions including edge cases (invalid currency XYZ, negative amount, high-value wire transfers, unusual-hour cross-border payment) to derive testable mid-level objectives. Uses Python stack with `decimal.Decimal`, ISO 4217 whitelist, file-based JSON messaging via `shared/` directories.

---

### Agent 2 — Code Generation Agent

| Field | Value |
|-------|-------|
| **File** | `agents/code_generation_agent.md` |
| **Role** | Generates the Python pipeline code from the specification |
| **Reads** | `specification.md`, `sample-transactions.json` |
| **Produces** | `integrator.py`, `agents/transaction_validator.py`, `agents/fraud_detector.py`, `agents/settlement_processor.py` |
| **Dependencies** | Agent 1 must complete first (`specification.md` must exist) |
| **MCP** | Uses context7 to look up Python `decimal` module and `fastmcp` library documentation |

**Project context**: Builds three cooperating pipeline agents that communicate via JSON files in `shared/input/`, `shared/processing/`, `shared/output/`, and `shared/results/`. All monetary arithmetic uses `decimal.Decimal`. Each agent exposes a `process_message(message: dict) -> dict` function. Documents context7 queries in `research-notes.md`.

---

### Agent 3 — Unit Test Agent

| Field | Value |
|-------|-------|
| **File** | `agents/unit_test_agent.md` |
| **Role** | Generates the test suite covering all pipeline agents |
| **Reads** | `specification.md`, `agents/transaction_validator.py`, `agents/fraud_detector.py`, `agents/settlement_processor.py` |
| **Produces** | `tests/test_transaction_validator.py`, `tests/test_fraud_detector.py`, `tests/test_settlement_processor.py`, `tests/test_integration.py` |
| **Dependencies** | Agent 2 must complete first (pipeline code must exist) |
| **Hook** | Coverage gate blocks `git push` if coverage < 80% |

**Project context**: Tests use `pytest` with `tmp_path` fixture to isolate from real `shared/` directories. Must cover: all 8 transaction edge cases, rejection reasons (INVALID_CURRENCY, INVALID_AMOUNT, MISSING_FIELD), fraud scoring thresholds, fee calculation, PII masking in logs. Target ≥ 90% coverage.

---

### Agent 4 — Documentation Agent

| Field | Value |
|-------|-------|
| **File** | `agents/documentation_agent.md` |
| **Role** | Generates README, HOWTORUN, and project documentation |
| **Reads** | `specification.md`, `agents.md`, all pipeline agent files, test results |
| **Produces** | `README.md`, `HOWTORUN.md` |
| **Dependencies** | Agents 2 and 3 must complete (pipeline and tests must exist) |
| **Requirement** | README must include the author's name ("Created by Ivan Batura") |

**Project context**: README must include: author name, system description (1–2 paragraphs), agent responsibilities (one bullet per agent), ASCII architecture diagram of the pipeline flow, tech stack table. HOWTORUN must have numbered steps from environment setup through running the pipeline and viewing results.

---

## Pipeline Agents (Output of Agent 2)

These are Python scripts produced by the Code Generation Agent. They are NOT sub-agents — they are the actual transaction processing system.

---

### Transaction Validator (`agents/transaction_validator.py`)

- **Input**: JSON message from `shared/input/`
- **Output**: Message with `status: "validated"` or `status: "rejected"` + `reason`
- **Checks**: Required fields, positive Decimal amount, ISO 4217 currency whitelist
- **Passes to**: `shared/output/` → Fraud Detector

### Fraud Detector (`agents/fraud_detector.py`)

- **Input**: Validated message from `shared/output/`
- **Output**: Message with `fraud_risk_score` (0–10), `fraud_risk_level` (LOW/MEDIUM/HIGH), `unusual_hour`, `cross_border`
- **Scoring**: +3 for >$10K, +4 for >$50K, +2 for 02:00–05:00 UTC, +1 for non-US
- **Passes to**: `shared/output/` → Settlement Processor

### Settlement Processor (`agents/settlement_processor.py`)

- **Input**: Fraud-scored message
- **Output**: Message with `fee_amount`, `settlement_status` (SETTLED/HELD_FOR_REVIEW/REJECTED)
- **Fee**: 0.1% of amount (min $0.50) + $25.00 surcharge for HIGH risk
- **Writes**: Final result to `shared/results/<transaction_id>.json`

---

## Directory Structure (Target End State)

```
homework-6/
├── sample-transactions.json        # input data (8 transactions)
├── specification.md                # produced by Agent 1
├── agents.md                       # this file
├── integrator.py                   # produced by Agent 2 — orchestrates the pipeline
├── research-notes.md               # context7 queries (Task 4)
├── mcp.json                        # MCP server config (context7 + pipeline-status)
├── agents/
│   ├── specification_agent.md      # Agent 1 sub-agent definition
│   ├── code_generation_agent.md    # Agent 2 sub-agent definition
│   ├── unit_test_agent.md          # Agent 3 sub-agent definition
│   ├── documentation_agent.md      # Agent 4 sub-agent definition
│   ├── transaction_validator.py    # pipeline agent (produced by Agent 2)
│   ├── fraud_detector.py           # pipeline agent (produced by Agent 2)
│   └── settlement_processor.py     # pipeline agent (produced by Agent 2)
├── mcp/
│   └── server.py                   # custom FastMCP server (Task 4)
├── tests/
│   ├── test_transaction_validator.py
│   ├── test_fraud_detector.py
│   ├── test_settlement_processor.py
│   └── test_integration.py
├── shared/
│   ├── input/
│   ├── processing/
│   ├── output/
│   └── results/
├── .claude/
│   └── commands/
│       ├── write-spec.md           # slash command (Task 1)
│       ├── run-pipeline.md         # slash command (Task 3)
│       └── validate-transactions.md # slash command (Task 3)
├── docs/
│   └── screenshots/
├── README.md
└── HOWTORUN.md
```
