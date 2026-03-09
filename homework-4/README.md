# Homework 4 — 4-Agent Bug-Fix Pipeline

**Student**: Ivan Batura
**Agent / Tool**: Claude Code (terminal in JetBrains IDEA)
**Model**: claude-sonnet-4-6

---

## Overview

This project demonstrates a **4-agent agentic pipeline** that automatically researches,
implements, security-reviews, and tests a bug fix — with each stage handled by a
dedicated sub-agent.

### Bug Fixed

**API-404** — `GET /api/users/:id` returned 404 for every valid user ID because
Express route parameters are strings while the in-memory `users` array stores IDs as
numbers. Strict equality (`===`) between `"123"` and `123` is always `false`, so every
lookup failed. The fix: add `parseInt(req.params.id, 10)` at the point of extraction.

---

## Pipeline

```
Bug Research Verifier
        |
        v
Bug Implementer
        |
       / \
      v   v
Security  Unit Test
Verifier  Generator
```

| Agent | File | Role |
|-------|------|------|
| Bug Research Verifier | `agents/research-verifier.agent.md` | Fact-checks codebase research; rates quality; produces `verified-research.md` |
| Bug Implementer | `agents/bug-implementer.agent.md` | Applies the implementation plan; runs tests; produces `fix-summary.md` |
| Security Vulnerabilities Verifier | `agents/security-verifier.agent.md` | Scans changed code for vulnerabilities; produces `security-report.md` |
| Unit Test Generator | `agents/unit-test-generator.agent.md` | Writes FIRST-compliant unit tests for changed code; produces `test-report.md` |

### Supporting Skills

| Skill | Used by |
|-------|---------|
| `skills/research-quality-measurement.md` | Bug Research Verifier |
| `skills/unit-tests-FIRST.md` | Unit Test Generator |

---

## Project Structure

```
homework-4/
├── README.md
├── HOWTORUN.md
├── STUDENT.md
├── agents/
│   ├── research-verifier.agent.md
│   ├── bug-implementer.agent.md
│   ├── security-verifier.agent.md
│   └── unit-test-generator.agent.md
├── skills/
│   ├── research-quality-measurement.md
│   └── unit-tests-FIRST.md
├── context/bugs/API-404/
│   ├── bug-context.md
│   ├── research/
│   │   ├── codebase-research.md
│   │   └── verified-research.md
│   ├── implementation-plan.md
│   ├── fix-summary.md
│   ├── security-report.md
│   └── test-report.md
├── server.js
├── src/
│   ├── controllers/userController.js
│   └── routes/users.js
├── package.json
├── tests/
│   └── userController.test.js
└── docs/screenshots/
```

---

## Pipeline Results Summary

| Stage | Output | Status |
|-------|--------|--------|
| Bug Research Verifier | `context/bugs/API-404/research/verified-research.md` | FAIL (ADEQUATE — one mismatch on the exact fix line) |
| Bug Implementer | `context/bugs/API-404/fix-summary.md` | COMPLETED |
| Security Vulnerabilities Verifier | `context/bugs/API-404/security-report.md` | MEDIUM risk (no CRITICAL/HIGH) |
| Unit Test Generator | `context/bugs/API-404/test-report.md` | COMPLETED — 5/5 tests pass |

---

## How to Run the App

```bash
cd homework-4
npm install
npm start
# Server starts on http://localhost:3000
```

Endpoints:
- `GET /health` — health check
- `GET /api/users` — list all users
- `GET /api/users/:id` — get user by ID (e.g. `/api/users/123`)

## How to Run the Tests

```bash
cd homework-4
npm install
npm test
```

---

## How to Run the Pipeline

See [HOWTORUN.md](HOWTORUN.md) for step-by-step pipeline execution instructions.
