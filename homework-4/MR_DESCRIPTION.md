# Homework 4 — 4-Agent Bug-Fix Pipeline

**Author**: Ivan Batura
**Branch**: `homework-4-submission` → `main`
**Model used**: claude-sonnet-4-6 (Claude Code, JetBrains IDEA terminal)

---

## Summary

This PR submits Homework 4: a fully working **4-agent agentic pipeline** that
researches, implements, security-reviews, and unit-tests a bug fix — each stage
handled by a dedicated sub-agent definition.

The demo application is a small Express.js API with a deliberately introduced
**API-404 bug**: `GET /api/users/:id` returned 404 for every valid ID because
Express delivers route params as strings while the in-memory store uses numeric
IDs — strict equality (`===`) between `"123"` and `123` is always `false`.

---

## What's Included

### Agents (`homework-4/agents/`)

| Agent file | Role |
|---|---|
| `research-verifier.agent.md` | Fact-checks codebase research; rates quality via skill; produces `verified-research.md` |
| `bug-implementer.agent.md` | Reads `implementation-plan.md`, applies changes, runs tests, produces `fix-summary.md` |
| `security-verifier.agent.md` | Scans changed files for vulnerabilities; rates CRITICAL → INFO; produces `security-report.md` |
| `unit-test-generator.agent.md` | Writes FIRST-compliant tests for changed code only; produces `test-report.md` |

### Supporting Skills (`homework-4/skills/`)

| Skill | Used by |
|---|---|
| `research-quality-measurement.md` | Bug Research Verifier — defines 5-level quality scale |
| `unit-tests-FIRST.md` | Unit Test Generator — defines Fast/Independent/Repeatable/Self-validating/Timely |

### Pipeline Artifacts (`homework-4/context/bugs/API-404/`)

| Artifact | Status |
|---|---|
| `research/codebase-research.md` | Input — original research |
| `research/verified-research.md` | **ADEQUATE** — one line-number mismatch flagged |
| `implementation-plan.md` | Input — step-by-step fix plan |
| `fix-summary.md` | **COMPLETED** — `parseInt` fix applied, tests pass |
| `security-report.md` | **MEDIUM** risk — no CRITICAL/HIGH findings |
| `test-report.md` | **COMPLETED** — 5/5 tests pass |

### Application (`homework-4/`)

- Express.js server (`server.js`, `src/`)
- Bug is fixed: `req.params.id` is now parsed with `parseInt(req.params.id, 10)`
- Jest test suite in `tests/userController.test.js`

---

## Pipeline Flow

```
Bug Research Verifier
        │
        ▼
Bug Implementer
        │
       ┌┴┐
       ▼ ▼
Security  Unit Test
Verifier  Generator
```

---

## How to Verify

```bash
cd homework-4
npm install
npm test        # 5 tests, all green
npm start       # server on http://localhost:3000
curl http://localhost:3000/api/users/123   # returns user JSON (was 404 before fix)
```

Full step-by-step pipeline instructions are in [HOWTORUN.md](HOWTORUN.md).

---

## Checklist

- [x] All 4 agent definitions submitted (`agents/`)
- [x] Two supporting skills submitted (`skills/`)
- [x] Bug fixed and verified with passing tests
- [x] All 4 pipeline output artifacts present (`context/bugs/API-404/`)
- [x] README and HOWTORUN written
- [x] STUDENT.md filled in
- [x] Agent definitions also registered in `.claude/agents/` for IDE use
