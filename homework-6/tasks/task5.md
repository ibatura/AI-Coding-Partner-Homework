# Task 5 — Agent 4: Testing & Documentation

## Overview
Agent 4 is the **Documentation Agent** — a **Claude sub-agent defined as a Markdown file**. When invoked, Claude reads this MD file's instructions and produces the README, HOWTORUN, and any remaining documentation. This task also covers the test suite (produced by Agent 3's sub-agent) and screenshot deliverables.

## Priority
⭐⭐ Required — depends on Tasks 1–4 (all pipeline code, skills, hooks, and MCP must exist).

## Subtasks

| Subtask | File | Description |
|---------|------|-------------|
| 5.1 | `task5.1.md` | Unit & Integration Tests (output of Agent 3 sub-agent) |
| 5.2 | `task5.2.md` | Documentation — README, HOWTORUN (output of Agent 4 sub-agent) |
| 5.3 | `task5.3.md` | Screenshots |

---

## Step 1: Create the Documentation Sub-Agent MD File

**Action**: Create `agents/documentation_agent.md`

This is the **first file to create** — a **Markdown file containing prompts and instructions for Claude**. It is NOT a Python script. When Claude reads and executes this file, it generates README.md and HOWTORUN.md.

**The MD file must contain**:
- **Context section**: Reference the specification, all agent source files, test results, pipeline architecture, and the student's name
- **Task section**: Instruct Claude to generate README.md and HOWTORUN.md
- **Rules section**: README MUST include the student's name, must have ASCII architecture diagram, must list all agent responsibilities, must include tech stack table
- **Output section**: Specify README.md and HOWTORUN.md as output files

**Example structure**:
```markdown
# Documentation Agent

## Context
Read the following files to understand the full system:
- specification.md — the technical specification
- agents/*.py — all pipeline agent code
- integrator.py — the orchestrator
- tests/ — the test suite
- mcp/server.py — the custom MCP server
- .claude/commands/ — the slash command skills
- .claude/settings.json — the hook configuration

## Task
Generate comprehensive project documentation:
1. README.md — project overview, architecture, setup
2. HOWTORUN.md — step-by-step execution guide

## Rules
- README MUST include: "Created by [Student Name]" prominently at the top
- README MUST include an ASCII architecture diagram showing the pipeline flow
- README MUST list responsibilities for all 4 meta-agents AND all 3 pipeline agents
- README MUST include a tech stack table
- HOWTORUN MUST have numbered steps from prerequisites through demo
- All instructions must be verified — follow your own steps

## Output
Create README.md and HOWTORUN.md in the project root.
```

---

## Directory Structure

```
project-root/
├── agents/
│   ├── documentation_agent.md   ← THE SUB-AGENT (MD file, created FIRST)
│   ├── specification_agent.md   ← from Task 1
│   ├── code_generation_agent.md ← from Task 2
│   ├── unit_test_agent.md       ← from Task 3
│   └── ... (Python output files)
├── tests/                        ← output of Agent 3 sub-agent
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_transaction_validator.py
│   ├── test_fraud_detector.py
│   ├── test_settlement_processor.py
│   └── test_integration.py
├── README.md                     ← OUTPUT of this agent
├── HOWTORUN.md                   ← OUTPUT of this agent
└── docs/
    └── screenshots/
        ├── pipeline-run.png
        ├── test-coverage.png
        ├── skill-run-pipeline.png
        ├── hook-trigger.png
        └── mcp-interaction.png
```

## Important Distinction
| What | Format | Purpose |
|------|--------|---------|
| `agents/documentation_agent.md` | Markdown (Claude sub-agent) | Instructions for Claude to generate docs |
| `README.md` | Markdown (output document) | Project documentation produced BY the agent |
| `HOWTORUN.md` | Markdown (output document) | Run guide produced BY the agent |

---

## Deliverables Checklist
- [ ] `agents/documentation_agent.md` — the sub-agent MD file (created **first**)
- [ ] `tests/` directory with all test files (subtask 5.1, output of Agent 3)
- [ ] Test coverage ≥ 80% (gate), aim ≥ 90% (subtask 5.1)
- [ ] `README.md` with student's name, description, diagram (subtask 5.2, output of Agent 4)
- [ ] `HOWTORUN.md` with step-by-step instructions (subtask 5.2, output of Agent 4)
- [ ] 5 screenshots in `docs/screenshots/` (subtask 5.3)
- [ ] PR description includes all screenshots

## Dependencies
- Tasks 1–4 (all code must exist to document)

## Feeds Into
- Final PR submission

## Summary of All 4 Sub-Agent MD Files

| Agent | MD File | Produces |
|-------|---------|----------|
| Agent 1 — Specification | `agents/specification_agent.md` | `specification.md`, `agents.md` |
| Agent 2 — Code Generation | `agents/code_generation_agent.md` | All Python pipeline code |
| Agent 3 — Unit Tests | `agents/unit_test_agent.md` | All test files in `tests/` |
| Agent 4 — Documentation | `agents/documentation_agent.md` | `README.md`, `HOWTORUN.md` |
