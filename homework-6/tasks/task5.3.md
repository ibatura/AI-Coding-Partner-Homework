# Task 5.3 — Screenshots

## Overview
Capture 5 required screenshots documenting each major step. Save all screenshots to `docs/screenshots/`. These same screenshots must also be included in the PR description.

---

## Step 1: Create Screenshots Directory
```bash
mkdir -p docs/screenshots
```

---

## Step 2: Capture Each Screenshot

### Screenshot 1: `pipeline-run.png`
- **What to capture**: Full terminal output of running the pipeline
- **How**: Run `python integrator.py` in terminal
- **Must show**: All 8 transactions being processed, final summary with counts
- **When**: After Task 2 is complete

### Screenshot 2: `test-coverage.png`
- **What to capture**: Coverage report showing ≥ 80% (gate) and ideally ≥ 90%
- **How**: Run `pytest --cov=agents --cov=integrator --cov-report=term-missing -v`
- **Must show**: Coverage percentages per module, overall percentage, all tests passing
- **When**: After Task 5.1 is complete

### Screenshot 3: `skill-run-pipeline.png`
- **What to capture**: The `/run-pipeline` Claude Code skill executing
- **How**: In Claude Code, type `/run-pipeline` and let it execute
- **Must show**: The skill being invoked, the pipeline running, results summary
- **When**: After Task 3.1 is complete

### Screenshot 4: `hook-trigger.png`
- **What to capture**: The coverage gate hook firing (blocking or allowing push)
- **How**: Attempt `git push` — the hook should run tests and show coverage
- **Must show**: The hook checking coverage, the pass/fail decision
- **When**: After Task 3.2 is complete
- **Tip**: To show a block, temporarily set threshold to 100% and push

### Screenshot 5: `mcp-interaction.png`
- **What to capture**: Both a context7 query result AND a custom MCP tool call
- **How**: In Claude Code, use context7 to look up a library, then call `get_transaction_status("TXN001")`
- **Must show**: context7 response with library info, and custom MCP tool returning transaction status
- **When**: After Task 4 is complete
- **Note**: This may need to be a composite/two-part screenshot

---

## Step 3: Include in PR Description

When creating the pull request, embed all screenshots in the PR description:
```markdown
## Screenshots

### Pipeline Run
![Pipeline Run](docs/screenshots/pipeline-run.png)

### Test Coverage
![Test Coverage](docs/screenshots/test-coverage.png)

### Skill Execution
![Skill Run Pipeline](docs/screenshots/skill-run-pipeline.png)

### Hook Trigger
![Hook Trigger](docs/screenshots/hook-trigger.png)

### MCP Interaction
![MCP Interaction](docs/screenshots/mcp-interaction.png)
```

---

## Files to Create
- `docs/screenshots/pipeline-run.png`
- `docs/screenshots/test-coverage.png`
- `docs/screenshots/skill-run-pipeline.png`
- `docs/screenshots/hook-trigger.png`
- `docs/screenshots/mcp-interaction.png`

## Dependencies
- All tasks (1–4) completed
- Tests passing with ≥ 80% coverage
- Skills and hooks configured
- MCP servers running

## Notes
- Screenshots must be actual captures, not mocked
- Each screenshot should clearly show the relevant output
- Terminal screenshots should have readable font size
- If a screenshot requires multiple captures (e.g., MCP interaction), combine them or take two separate shots
