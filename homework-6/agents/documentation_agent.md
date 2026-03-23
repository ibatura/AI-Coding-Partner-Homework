# Documentation Agent

## Context

Read the following files to understand the full system before generating documentation:

- `specification.md` — the technical specification (5 sections: objective, mid-level objectives, implementation notes, context, test requirements)
- `agents.md` — meta-agent definitions and pipeline agent descriptions
- `agents/transaction_validator.py` — Agent 1 of the pipeline: validates transactions
- `agents/fraud_detector.py` — Agent 2 of the pipeline: scores fraud risk
- `agents/settlement_processor.py` — Agent 3 of the pipeline: settles transactions
- `agents/base_agent.py` — shared base class for all pipeline agents
- `integrator.py` — the orchestrator that runs all three pipeline agents end-to-end
- `tests/conftest.py` — shared pytest fixtures
- `tests/test_transaction_validator.py` — unit tests for the validator
- `tests/test_fraud_detector.py` — unit tests for the fraud detector
- `tests/test_settlement_processor.py` — unit tests for the settlement processor
- `tests/test_integration.py` — end-to-end integration tests
- `mcp/server.py` — the custom FastMCP server exposing pipeline status tools
- `.claude/commands/write-spec.md` — slash command for spec generation
- `.claude/commands/run-pipeline.md` — slash command for pipeline execution
- `.claude/commands/validate-transactions.md` — slash command for dry-run validation
- `.claude/settings.json` — hook configuration (PrePush coverage check)
- `sample-transactions.json` — 8 raw transactions used as pipeline input

The student who built this system is **Ivan Batura**.

## Task

Generate comprehensive project documentation by creating two files:

1. **README.md** — project overview, architecture diagram, agent responsibilities, tech stack, and setup instructions
2. **HOWTORUN.md** — step-by-step execution guide from prerequisites through a full demo run

## Rules

### README.md Rules
- MUST include `Created by Ivan Batura` prominently at the top (within the first 5 lines)
- MUST include an ASCII architecture diagram showing the full pipeline flow:
  - `sample-transactions.json` → `integrator.py` → `shared/input/` → Transaction Validator → `shared/processing/` → Fraud Detector → `shared/output/` → Settlement Processor → `shared/results/`
  - Also show the MCP server reading from `shared/results/`
  - Show rejected transactions going directly to `shared/results/`
- MUST list responsibilities for all **4 meta-agents**:
  - Agent 1 — Specification Agent (`agents/specification_agent.md`)
  - Agent 2 — Code Generation Agent (`agents/code_generation_agent.md`)
  - Agent 3 — Unit Test Agent (`agents/unit_test_agent.md`)
  - Agent 4 — Documentation Agent (`agents/documentation_agent.md`)
- MUST list responsibilities for all **3 pipeline agents**:
  - Transaction Validator (`agents/transaction_validator.py`)
  - Fraud Detector (`agents/fraud_detector.py`)
  - Settlement Processor (`agents/settlement_processor.py`)
- MUST include a tech stack table with columns: Component, Technology, Purpose
- MUST include a Features section summarising key capabilities (PII masking, ISO 4217 enforcement, Decimal arithmetic, file-based IPC, audit logging)
- MUST include a Project Structure section

### HOWTORUN.md Rules
- MUST have numbered steps beginning with prerequisites (Python 3.9+, pip)
- MUST cover: clone repo, install dependencies, run the pipeline, run the tests, check coverage, start the MCP server, use slash commands
- Steps must be self-contained and verified — follow your own instructions
- Include expected output snippets where helpful
- Include a troubleshooting section for common issues

## Output

Create these two files in the project root (`homework-6/`):
- `README.md`
- `HOWTORUN.md`