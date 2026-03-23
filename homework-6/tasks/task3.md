# Task 3 — Agent 3: Skills & Hooks

## Overview
Agent 3 is the **Unit Test Agent** — a **Claude sub-agent defined as a Markdown file**. When invoked, Claude reads this MD file's instructions and generates the test suite for the pipeline. This task also creates 2 custom Claude Code skills (slash commands) and 1 required hook that blocks `git push` if test coverage is below 80%.

## Priority
⭐⭐ Required — depends on Task 2 (pipeline must exist to run/validate).

## Subtasks

| Subtask | File | Description |
|---------|------|-------------|
| 3.1 | `task3.1.md` | Custom Skills (2 slash commands) |
| 3.2 | `task3.2.md` | Coverage Gate Hook |

---

## Step 1: Create the Unit Test Sub-Agent MD File

**Action**: Create `agents/unit_test_agent.md`

This is the **first file to create** — a **Markdown file containing prompts and instructions for Claude**. It is NOT a Python script. When Claude reads and executes this file, it generates the test suite.

**The MD file must contain**:
- **Context section**: Reference the pipeline code (all agent .py files, integrator.py), the specification, and the sample transactions
- **Task section**: Instruct Claude to generate a comprehensive pytest test suite with ≥ 80% coverage (target ≥ 90%)
- **Rules section**: Use `tmp_path` for isolation, never write to real `shared/`, cover all validation branches, all risk scoring paths, all settlement logic, include integration tests
- **Output section**: List every test file to create in the `tests/` directory

**Example structure**:
```markdown
# Unit Test Agent

## Context
The banking pipeline is implemented in Python with these files:
- agents/base_agent.py — shared base class
- agents/transaction_validator.py — validates transactions
- agents/fraud_detector.py — scores fraud risk
- agents/settlement_processor.py — settles transactions
- integrator.py — orchestrates the pipeline
Read each file to understand the code before writing tests.

## Task
Generate a comprehensive test suite in tests/ with:
- tests/conftest.py — shared fixtures using tmp_path
- tests/test_transaction_validator.py — unit tests for validator
- tests/test_fraud_detector.py — unit tests for fraud scoring
- tests/test_settlement_processor.py — unit tests for settlement
- tests/test_base_agent.py — unit tests for base class
- tests/test_integration.py — end-to-end pipeline test

## Rules
- Use pytest and pytest-cov
- All tests must use tmp_path for shared/ directories (NEVER write to real shared/)
- Cover every validation rule, every risk scoring path, every settlement branch
- Test edge cases from sample data: TXN006 (bad currency), TXN007 (negative amount)
- Target ≥ 90% code coverage

## Output
Create all test files listed above. Tests must pass via: pytest -v --cov=agents --cov-report=term-missing
```

---

## Directory Structure to Create

```
project-root/
├── agents/
│   ├── unit_test_agent.md       ← THE SUB-AGENT (MD file, created FIRST)
│   ├── specification_agent.md   ← from Task 1
│   ├── code_generation_agent.md ← from Task 2
│   └── ... (Python output files)
├── .claude/
│   ├── commands/
│   │   ├── write-spec.md           ← from Task 1
│   │   ├── run-pipeline.md         ← subtask 3.1
│   │   └── validate-transactions.md ← subtask 3.1
│   └── settings.json               ← subtask 3.2 (hooks)
├── tests/                           ← OUTPUT of this agent
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_transaction_validator.py
│   ├── test_fraud_detector.py
│   ├── test_settlement_processor.py
│   ├── test_base_agent.py
│   └── test_integration.py
└── docs/
    └── screenshots/
        ├── skill-run-pipeline.png   ← screenshot deliverable
        └── hook-trigger.png         ← screenshot deliverable
```

## Important Distinction
| What | Format | Purpose |
|------|--------|---------|
| `agents/unit_test_agent.md` | Markdown (Claude sub-agent) | Instructions for Claude to generate the test suite |
| `tests/*.py` | Python (output code) | Actual test files produced BY the agent |
| `.claude/commands/*.md` | Markdown (slash commands) | Skills that automate pipeline operations |
| `.claude/settings.json` | JSON (config) | Hook configuration for coverage gate |

---

## Deliverables Checklist
- [ ] `agents/unit_test_agent.md` — the sub-agent MD file (created **first**)
- [ ] `.claude/commands/run-pipeline.md` (subtask 3.1)
- [ ] `.claude/commands/validate-transactions.md` (subtask 3.1)
- [ ] `.claude/settings.json` with coverage gate hook (subtask 3.2)
- [ ] `docs/screenshots/skill-run-pipeline.png` — screenshot of `/run-pipeline` executing
- [ ] `docs/screenshots/hook-trigger.png` — screenshot of hook firing

## Dependencies
- Task 1 (write-spec.md skill already created)
- Task 2 (pipeline code must exist for skills to invoke and for tests to cover)

## Feeds Into
- Task 5 (tests are the output of this agent, coverage gate protects quality)
