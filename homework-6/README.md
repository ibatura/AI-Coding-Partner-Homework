# AI-Powered Multi-Agent Banking Transaction Pipeline

**Created by Ivan Batura**

A 3-agent Python pipeline that validates, scores for fraud risk, and settles banking transactions — built entirely by Claude sub-agents using file-based JSON message passing, full audit logging, PII masking, and ISO 4217 currency enforcement.

---

## Architecture

```
  sample-transactions.json
           |
           v
   +------------------+
   |  integrator.py   |  <-- orchestrates the full pipeline
   +--------+---------+
            |
            |  writes message envelopes to shared/input/
            v
  +-------------------------+        +------------------+
  | Transaction Validator   |        |                  |
  |  (transaction_          |---+--->| shared/results/  |
  |   validator.py)         | reject |  (rejected txns) |
  +----------+--------------+   |    +------------------+
             |                  |
             | valid txns to shared/processing/
             v
  +-------------------------+
  |    Fraud Detector        |
  |  (fraud_detector.py)     |
  +----------+---------------+
             |
             | scored txns to shared/output/
             v
  +-------------------------+        +------------------+
  | Settlement Processor     |        |                  |
  |  (settlement_processor.  |------->| shared/results/  |
  |   py)                    | settle |  (final results) |
  +-------------------------+        +------------------+
                                             ^
                                             |  reads results
                                    +--------+-------+
                                    |   MCP Server   |
                                    | (mcp/server.py)|
                                    +----------------+
                                     FastMCP tools:
                                     - get_transaction_status
                                     - list_pipeline_results
                                     - get_pipeline_stats
```

---

## Meta-Agents (Claude Sub-Agents)

These Markdown files contain instructions for Claude. Each agent reads source files and produces outputs — they are not Python scripts.

| Agent | File | Role | Produces |
|-------|------|------|----------|
| Agent 1 — Specification | `agents/specification_agent.md` | Analyzes 8 sample transactions and derives testable mid-level objectives | `specification.md`, `agents.md` |
| Agent 2 — Code Generation | `agents/code_generation_agent.md` | Generates all Python pipeline code from the specification | `integrator.py`, `agents/*.py` |
| Agent 3 — Unit Tests | `agents/unit_test_agent.md` | Generates a full pytest test suite targeting ≥ 90% coverage | `tests/test_*.py`, `tests/conftest.py` |
| Agent 4 — Documentation | `agents/documentation_agent.md` | Generates project documentation | `README.md`, `HOWTORUN.md` |

---

## Pipeline Agents

These Python modules do the actual transaction processing at runtime.

### Transaction Validator (`agents/transaction_validator.py`)
- Reads message envelopes from `shared/input/`
- Validates currency code against ISO 4217 whitelist: `['USD', 'EUR', 'GBP', 'JPY']`
- Rejects transactions with invalid currency (`INVALID_CURRENCY`) or non-positive amount (`INVALID_AMOUNT`)
- Masks account numbers in all log output (e.g. `ACC-1001` → `ACC-***1`)
- Writes validated messages to `shared/processing/`; rejected messages to `shared/results/`

### Fraud Detector (`agents/fraud_detector.py`)
- Reads validated messages from `shared/processing/`
- Assigns a `fraud_risk_score` (0–10) and `fraud_risk_level` (`LOW`, `MEDIUM`, `HIGH`)
- Applies +2 score penalty for transactions processed between 02:00–05:00 UTC (`unusual_hour: true`)
- Flags transactions above $10,000 as `MEDIUM` risk (score 3–6); above $50,000 as `HIGH` risk (score ≥ 7)
- Writes scored messages to `shared/output/`

### Settlement Processor (`agents/settlement_processor.py`)
- Reads fraud-scored messages from `shared/output/`
- Calculates fee using `decimal.Decimal` arithmetic (0.1% base fee, surcharges for HIGH risk)
- Sets `settlement_status` to `settled`, `settled_with_review`, or `held_for_review`
- Writes final result records to `shared/results/`

---

## Features

| Feature | Detail |
|---------|--------|
| PII masking | Account numbers masked to last-4 format in all audit logs |
| ISO 4217 enforcement | Only `USD`, `EUR`, `GBP`, `JPY` accepted; all others rejected |
| Decimal arithmetic | All monetary values use `decimal.Decimal`; no floats |
| File-based IPC | Agents communicate exclusively through JSON files in `shared/` |
| Audit logging | Every agent writes ISO 8601 timestamped log entries with outcome |
| MCP server | FastMCP server exposes 3 tools to query transaction results |
| Slash commands | `/write-spec`, `/run-pipeline`, `/validate-transactions` |
| Pre-push hook | Blocks push if test coverage falls below 80% |

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Runtime | Python 3.9+ | Pipeline agents and integrator |
| Monetary math | `decimal.Decimal` | Exact currency arithmetic, no float rounding |
| Agent framework | Custom `BaseAgent` | Shared lifecycle and logging for all pipeline agents |
| MCP server | FastMCP | Exposes pipeline results as MCP tools |
| Test framework | pytest | Unit and integration test suite |
| Coverage | pytest-cov | Enforces ≥ 80% coverage via pre-push hook |
| Slash commands | Claude Code `.claude/commands/` | One-command pipeline and spec generation |
| Hooks | Claude Code `settings.json` | PrePush coverage gate |
| IPC format | JSON files in `shared/` | Decoupled inter-agent message passing |

---

## Project Structure

```
homework-6/
├── agents/
│   ├── base_agent.py                  # Shared agent base class
│   ├── transaction_validator.py       # Pipeline Agent 1
│   ├── fraud_detector.py              # Pipeline Agent 2
│   ├── settlement_processor.py        # Pipeline Agent 3
│   ├── specification_agent.md         # Meta-Agent 1 (Claude instructions)
│   ├── code_generation_agent.md       # Meta-Agent 2 (Claude instructions)
│   ├── unit_test_agent.md             # Meta-Agent 3 (Claude instructions)
│   └── documentation_agent.md        # Meta-Agent 4 (Claude instructions)
├── tests/
│   ├── conftest.py                    # Shared pytest fixtures
│   ├── test_transaction_validator.py
│   ├── test_fraud_detector.py
│   ├── test_settlement_processor.py
│   ├── test_base_agent.py
│   └── test_integration.py
├── mcp/
│   └── server.py                      # FastMCP server
├── shared/                            # Runtime IPC directories (auto-created)
│   ├── input/                         # Raw message envelopes
│   ├── processing/                    # Validated transactions
│   ├── output/                        # Fraud-scored transactions
│   └── results/                       # Final settlement results
├── scripts/
│   └── check-coverage.sh              # Coverage gate script (used by pre-push hook)
├── .claude/
│   ├── commands/
│   │   ├── write-spec.md              # /write-spec slash command
│   │   ├── run-pipeline.md            # /run-pipeline slash command
│   │   └── validate-transactions.md  # /validate-transactions slash command
│   └── settings.json                  # Hook configuration
├── integrator.py                      # Pipeline orchestrator
├── sample-transactions.json           # 8 sample input transactions
├── specification.md                   # Technical specification
├── agents.md                          # Meta-agent definitions
├── mcp.json                           # MCP server configuration
├── README.md                          # This file
└── HOWTORUN.md                        # Step-by-step run guide
```

---

## Quick Start

```bash
cd homework-6
pip install -r requirements.txt      # or: pip install fastmcp pytest pytest-cov
python integrator.py                 # run the full pipeline
pytest --cov=agents tests/           # run tests with coverage
```

See [HOWTORUN.md](HOWTORUN.md) for the full step-by-step guide.
