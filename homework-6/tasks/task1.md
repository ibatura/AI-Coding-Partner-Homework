# Task 1 — Agent 1: Write the Specification

## Overview
Agent 1 is the **Specification Agent** — a **Claude sub-agent defined as a Markdown file**. When invoked, Claude reads this MD file's instructions and produces the detailed technical specification. This task is foundational — everything downstream (code, tests, docs) derives from the spec.

## Priority
⭐⭐ Required — must be completed **first** before any other task.

---

## Step 1: Create the Specification Sub-Agent MD File

**Action**: Create `agents/specification_agent.md`

This is a **Markdown file containing prompts and instructions for Claude**. It is NOT a Python script. When Claude reads and executes this file, it generates `specification.md`.

**The MD file must contain**:
- **Context section**: Describe what exists (project root, `sample-transactions.json`, `specification-TEMPLATE-hint.md`, directory structure)
- **Task section**: Instruct Claude to generate a complete `specification.md` following the template
- **Rules section**: Non-negotiable constraints (Decimal types, ISO 4217, audit logging, PII masking, file-based messaging)
- **Examples section**: Show sample input/output for the spec (a mid-level objective example, a low-level task example)
- **Output section**: Specify the output format — a single `specification.md` file with all 5 sections populated

**Example structure of the MD file**:
```markdown
# Specification Agent

## Context
You are a specification agent for an AI-powered multi-agent banking pipeline.
The project root contains `sample-transactions.json` with 8 raw transaction records.
Use `specification-TEMPLATE-hint.md` as the template structure.

## Task
Generate a complete `specification.md` with all 5 required sections...

## Rules
- All monetary values must use decimal.Decimal, never float
- Currency validation uses ISO 4217 whitelist
- Account numbers are PII — must be masked in logs
...

## Output
Write the specification to `specification.md` in the project root.
```

---

## Step 2: Write `specification.md` (the OUTPUT of Agent 1)

When the sub-agent runs, it produces `specification.md` with **all 5 sections**:

### Section 1 — High-Level Objective
One sentence describing the full pipeline:
- Must mention: multi-agent, Python, file-based JSON message passing, validation, fraud detection, and a third agent (Settlement Processor recommended)

### Section 2 — Mid-Level Objectives (4–5 testable items)
Must be concrete and testable. Derive these from the sample data:
- TXN006 has currency "XYZ" → objective about invalid currency rejection
- TXN007 has amount "-100.00" → objective about negative amount rejection
- TXN002 ($25,000) and TXN005 ($75,000) → objective about fraud flagging thresholds
- TXN004 timestamp 02:47 → objective about unusual-hour detection
- All 8 transactions → objective about end-to-end processing count
- Results written to `shared/results/` → objective about output format

### Section 3 — Implementation Notes
Must cover:
- `decimal.Decimal` for all monetary calculations (never `float`)
- ISO 4217 currency whitelist: at minimum USD, EUR, GBP, JPY
- Audit logging: ISO 8601 timestamps, agent name, transaction_id, outcome
- PII masking: account numbers masked in logs (e.g., `ACC-***1`)
- File-based communication via `shared/` directories
- JSON message format with required fields: message_id, timestamp, source_agent, target_agent, message_type, data
- Error handling: agents must not crash on malformed input; write rejection reason instead

### Section 4 — Context
- **Beginning state**: `sample-transactions.json` with 8 records. No agents, no `shared/` dirs.
- **Ending state**: All 8 transactions processed. Results in `shared/results/`. Each result is a JSON file. Test coverage ≥ 90%. README and HOWTORUN complete.

### Section 5 — Low-Level Tasks
One entry per pipeline agent (validator, fraud detector, 3rd agent), each with:
- **Task name**
- **Prompt**: The exact AI prompt to give Claude Code
- **File to CREATE**: path in `agents/` directory (these ARE Python files — the pipeline code)
- **Function to CREATE**: `process_message(message: dict) -> dict`
- **Details**: What the agent checks, transforms, or decides

Pipeline agents to specify:
1. **Transaction Validator** — field validation, amount checks, currency whitelist
2. **Fraud Detector** — risk scoring (0–10 scale), threshold-based flagging
3. **Settlement Processor** (recommended 3rd agent) — calculates fees, determines settlement status, writes final records

---

## Step 3: Write `agents.md`

- Define all 4 **meta-agents** (Claude sub-agents) and their roles:
  1. **Specification Agent** (`agents/specification_agent.md`) — generates the spec
  2. **Code Generation Agent** (`agents/code_generation_agent.md`) — generates pipeline Python code
  3. **Unit Test Agent** (`agents/unit_test_agent.md`) — generates the test suite
  4. **Documentation Agent** (`agents/documentation_agent.md`) — generates README and docs
- For each: name, role, MD file location, inputs it reads, outputs it produces, dependencies on other agents
- Include project-specific context: Python stack, file-based messaging, directory structure

---

## Step 4: Create the Slash Command Skill

**File**: `.claude/commands/write-spec.md`

This is a **Claude Code slash command** (also an MD file). When the user types `/write-spec`, Claude executes these instructions:
1. Read `specification-TEMPLATE-hint.md`
2. Read `sample-transactions.json`
3. Read `agents/specification_agent.md` to get the sub-agent's full instructions
4. Generate a complete `specification.md` following the template
5. Populate all 5 sections with project-specific content
6. Save the output to `specification.md` in the project root

---

## Deliverables Checklist
- [ ] `agents/specification_agent.md` — the sub-agent MD file (created **first**)
- [ ] `specification.md` — complete spec with all 5 sections (the OUTPUT of the agent)
- [ ] `agents.md` — extended with project-specific context for all 4 sub-agents
- [ ] `.claude/commands/write-spec.md` — slash command skill

## Dependencies
- None (this is the first task)

## Feeds Into
- Task 2 (code generation agent reads spec as input)
- Task 3 (skills reference spec structure)
- Task 5 (documentation agent references spec)

## Key Risks
- Vague mid-level objectives lead to ambiguous code in Task 2
- Missing edge cases in spec means missing test cases in Task 5
- Prompt quality in Low-Level Tasks directly affects Agent 2's code output

## Important Distinction
| What | Format | Purpose |
|------|--------|---------|
| `agents/specification_agent.md` | Markdown (Claude sub-agent) | Instructions for Claude to generate the spec |
| `specification.md` | Markdown (output document) | The actual specification produced by the agent |
| `.claude/commands/write-spec.md` | Markdown (slash command) | Skill that triggers spec generation |

## Sample Data Analysis (reference for spec writing)

| TXN ID | Amount     | Currency | Time  | Edge Case                          |
|--------|-----------|----------|-------|------------------------------------|
| TXN001 | 1,500.00  | USD      | 09:00 | Normal transaction                 |
| TXN002 | 25,000.00 | USD      | 09:15 | High value (>$10K fraud flag)      |
| TXN003 | 9,999.99  | USD      | 09:30 | Just under $10K threshold          |
| TXN004 | 500.00    | EUR      | 02:47 | Unusual hour + cross-border (DE)   |
| TXN005 | 75,000.00 | USD      | 10:00 | Very high value (>$50K fraud flag) |
| TXN006 | 200.00    | XYZ      | 10:05 | Invalid currency code              |
| TXN007 | -100.00   | GBP      | 10:10 | Negative amount + cross-border     |
| TXN008 | 3,200.00  | USD      | 10:15 | Normal transaction                 |
