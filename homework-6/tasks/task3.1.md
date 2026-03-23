# Task 3.1 — Custom Skills (Slash Commands)

## Overview
Create 2 custom Claude Code slash commands that automate common pipeline operations. These are **Markdown files** in `.claude/commands/` — not Python scripts.

**Note**: The skills are separate from the sub-agent MD files in `agents/`. Skills live in `.claude/commands/` and are invoked via Claude Code's `/command` syntax. Sub-agents live in `agents/` and are invoked by Claude reading their instructions.

---

## Skill 1: `/run-pipeline`

### Step 1: Create the Skill File
**Action**: Create `.claude/commands/run-pipeline.md`

### Step 2: Write the Skill Content

The file must be a Markdown document that Claude Code interprets as instructions when the user types `/run-pipeline`.

**Required behavior** (the skill must instruct Claude to do all of these):

1. **Check prerequisites**: Verify `sample-transactions.json` exists in the project root. If not, report an error.
2. **Clear shared/ directories**: Remove all files from `shared/input/`, `shared/processing/`, `shared/output/`, and `shared/results/` to ensure a clean run.
3. **Run the pipeline**: Execute `python integrator.py` (or the equivalent command for the chosen stack).
4. **Show results summary**: After the pipeline completes, read files from `shared/results/` and display:
   - Total transactions processed
   - How many settled, settled with review, held for review, rejected
   - Total fees collected
5. **Report rejected transactions**: For any rejected transactions, show the transaction ID and the rejection reason.

### Step 3: Skill File Format
```markdown
Run the multi-agent banking pipeline end-to-end.

Steps:
1. Check that sample-transactions.json exists
2. Clear shared/ directories
3. Run the pipeline (python integrator.py)
4. Show a summary of results from shared/results/
5. Report any transactions that were rejected and why
```

The actual file can be more detailed — include specifics about expected file paths and output format.

---

## Skill 2: `/validate-transactions`

### Step 1: Create the Skill File
**Action**: Create `.claude/commands/validate-transactions.md`

### Step 2: Write the Skill Content

**Required behavior**:

1. **Run validator in dry-run mode**: Execute `python agents/transaction_validator.py --dry-run` (or equivalent)
2. **Report results**: Display:
   - Total transaction count
   - Valid count
   - Invalid count
   - For each invalid transaction: ID, reason for rejection
3. **Show as table**: Format output as a readable table

### Step 3: Skill File Format
```markdown
Validate all transactions in sample-transactions.json without processing them.

Steps:
1. Run the validator in dry-run mode (python agents/transaction_validator.py --dry-run)
2. Report: total count, valid count, invalid count, reasons for rejection
3. Show a table of results
```

---

## Distinction: Skills vs Sub-Agents vs Pipeline Code

| File | Location | Type | Invoked via |
|------|----------|------|-------------|
| `run-pipeline.md` | `.claude/commands/` | Slash command skill | `/run-pipeline` in Claude Code |
| `validate-transactions.md` | `.claude/commands/` | Slash command skill | `/validate-transactions` in Claude Code |
| `write-spec.md` | `.claude/commands/` | Slash command skill | `/write-spec` in Claude Code |
| `specification_agent.md` | `agents/` | Claude sub-agent | Claude reads and executes instructions |
| `code_generation_agent.md` | `agents/` | Claude sub-agent | Claude reads and executes instructions |
| `unit_test_agent.md` | `agents/` | Claude sub-agent | Claude reads and executes instructions |
| `documentation_agent.md` | `agents/` | Claude sub-agent | Claude reads and executes instructions |
| `transaction_validator.py` | `agents/` | Python code (output) | `python integrator.py` |

---

## Screenshot Requirement
After creating both skills:
- Run `/run-pipeline` in Claude Code
- Capture a screenshot of the execution output
- Save as `docs/screenshots/skill-run-pipeline.png`

---

## Files to Create
- `.claude/commands/run-pipeline.md`
- `.claude/commands/validate-transactions.md`

## Dependencies
- Task 2 (pipeline Python code must be runnable)
- `agents/transaction_validator.py` must support `--dry-run` flag (subtask 2.1)

## Feeds Into
- Screenshot deliverable for Task 5
