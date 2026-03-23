# Task 3.2 — Coverage Gate Hook

## Overview
Create a Claude Code hook that **blocks `git push`** if unit test coverage is below 80%. This is a mandatory requirement for Agent 3 (the Unit Test sub-agent).

---

## Step 1: Create the Settings File
**Action**: Create `.claude/settings.json`

This file configures Claude Code hooks. The hook must:
- Trigger on `pre-push` (before `git push` completes)
- Run the test suite with coverage measurement
- Parse the coverage report
- **Block the push** if coverage is below 80%
- Allow the push if coverage is ≥ 80%

---

## Step 2: Hook Configuration

The `.claude/settings.json` should define hooks in the Claude Code format:

```json
{
  "hooks": {
    "pre-push": [
      {
        "command": "bash scripts/check-coverage.sh",
        "description": "Verify test coverage is at least 80% before pushing"
      }
    ]
  }
}
```

**Alternative**: The hook can be configured as a `PrePush` event hook with a shell command that runs pytest with coverage.

---

## Step 3: Create the Coverage Check Script

**Action**: Create `scripts/check-coverage.sh`

The script must:
1. Run `pytest --cov=agents --cov=integrator --cov-report=term-missing --cov-fail-under=80`
2. Capture the exit code
3. If pytest exits with 0 (coverage ≥ 80%): print success message, exit 0
4. If pytest exits non-zero (coverage < 80% or tests fail): print failure message with actual coverage %, exit 1
5. Make the script executable (`chmod +x`)

### Script outline:
```bash
#!/bin/bash
echo "Running coverage check..."
pytest --cov=agents --cov-report=term-missing --cov-fail-under=80
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "PUSH BLOCKED: Test coverage is below 80% or tests failed."
    echo "Fix failing tests or add more test coverage before pushing."
    exit 1
fi
echo "Coverage check passed. Push allowed."
exit 0
```

---

## Step 4: Alternative — Direct Hook Command

Instead of a separate script, the hook can run the command directly:

```json
{
  "hooks": {
    "pre-push": [
      {
        "command": "pytest --cov=agents --cov-report=term-missing --cov-fail-under=80",
        "description": "Block push if test coverage is below 80%"
      }
    ]
  }
}
```

Choose whichever approach is cleaner. The script approach is recommended for adding custom error messages.

---

## Step 5: Test the Hook

To verify the hook works:
1. Intentionally set `--cov-fail-under=100` (should fail with current coverage)
2. Attempt a `git push` — verify it is blocked
3. Reset to `--cov-fail-under=80`
4. Ensure tests pass at ≥ 80% coverage
5. Attempt a `git push` — verify it succeeds

---

## Relationship to Sub-Agents

The coverage gate hook works alongside the **Unit Test sub-agent** (`agents/unit_test_agent.md`):
- The sub-agent generates the test files (Python code in `tests/`)
- The hook runs those tests and enforces the coverage threshold
- Together they form Agent 3's complete deliverable

---

## Screenshot Requirement
- Trigger the hook (either by pushing or simulating)
- Capture the output showing the hook firing
- Save as `docs/screenshots/hook-trigger.png`

---

## Files to Create
- `.claude/settings.json` (with hook configuration)
- `scripts/check-coverage.sh` (optional, if using script approach)

## Dependencies
- Task 5.1 / Agent 3 output (test files in `tests/` must exist to measure coverage)
- `pytest` and `pytest-cov` must be installed

## Notes
- The hook should work with both `pytest` (Python) or equivalent for other stacks
- Consider also adding a `pre-commit` hook for running linting (optional, not required)
- The 80% threshold is the minimum gate; the spec aims for 90%+
