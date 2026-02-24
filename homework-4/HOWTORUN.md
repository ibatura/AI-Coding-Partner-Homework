# How to Run — Homework 4

---

## Prerequisites

- **Node.js** ≥ 18 and **npm** installed
- **Claude Code** CLI installed (`npm install -g @anthropic/claude-code` or via the
  JetBrains IDEA plugin)
- An `ANTHROPIC_API_KEY` environment variable set

---

## 1. Run the Demo Application

```bash
cd homework-4
npm install
npm start
```

The server starts on `http://localhost:3000`. Verify it works:

```bash
# Health check
curl http://localhost:3000/health

# List all users
curl http://localhost:3000/api/users

# Get user by ID (fixed endpoint)
curl http://localhost:3000/api/users/123
curl http://localhost:3000/api/users/456

# Non-existent ID → 404
curl http://localhost:3000/api/users/999
```

---

## 2. Run Unit Tests

```bash
cd homework-4
npm test
```

Expected output: 5 tests pass (`tests/userController.test.js`).

---

## 3. Run the 4-Agent Pipeline

The pipeline is run using **Claude Code** with sub-agent prompts. Each agent reads
its input files from `context/bugs/API-404/` and writes its output there.

### Step 0 — Prepare bug context

The bug context is already in place at `context/bugs/API-404/bug-context.md`.
A Bug Researcher has already produced `context/bugs/API-404/research/codebase-research.md`.

### Step 1 — Bug Research Verifier

In Claude Code (terminal in IDEA), run:

```
> Use the agent defined in agents/research-verifier.agent.md.
  Input: context/bugs/API-404/research/codebase-research.md
  Output: context/bugs/API-404/research/verified-research.md
```

Or invoke via the Task tool if orchestrating programmatically:
```
subagent_type: Bug Research Verifier
prompt: "Read context/bugs/API-404/research/codebase-research.md, verify all
         references against the source, and produce
         context/bugs/API-404/research/verified-research.md using the
         research-quality-measurement skill."
```

### Step 2 — Bug Implementer

After the verifier produces `verified-research.md`, the Bug Planner creates
`context/bugs/API-404/implementation-plan.md`. Then run the implementer:

```
> Use the agent defined in agents/bug-implementer.agent.md.
  Input: context/bugs/API-404/implementation-plan.md
  Output: context/bugs/API-404/fix-summary.md
```

### Step 3a — Security Vulnerabilities Verifier

After the implementer completes:

```
> Use the agent defined in agents/security-verifier.agent.md.
  Input: context/bugs/API-404/fix-summary.md + changed source files
  Output: context/bugs/API-404/security-report.md
```

### Step 3b — Unit Test Generator

Run in parallel with (or after) the security verifier:

```
> Use the agent defined in agents/unit-test-generator.agent.md.
  Input: context/bugs/API-404/fix-summary.md + changed source files
  Output: tests/userController.test.js + context/bugs/API-404/test-report.md
```

---

## 4. Reviewing Pipeline Outputs

| File | Description |
|------|-------------|
| `context/bugs/API-404/research/codebase-research.md` | Bug Researcher output |
| `context/bugs/API-404/research/verified-research.md` | Verification result + quality rating |
| `context/bugs/API-404/implementation-plan.md` | Fix plan (Bug Planner) |
| `context/bugs/API-404/fix-summary.md` | Applied changes + test results |
| `context/bugs/API-404/security-report.md` | Security findings |
| `context/bugs/API-404/test-report.md` | Unit test results + FIRST compliance |
| `tests/userController.test.js` | Generated unit tests |

---

## 5. Screenshots

Pipeline run screenshots are stored in `docs/screenshots/`.
