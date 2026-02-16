# Agent Configuration — Personal Financial Management Module

> This file defines how AI coding agents should behave when working on the PFM module. Feed this to any AI assistant (Claude Code, Copilot, Cursor, etc.) before starting implementation tasks.

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Project** | Personal Financial Management (PFM) Module |
| **Domain** | FinTech / Retail Banking |
| **Module location** | `pfm/` within the existing banking monorepo |
| **Primary language** | Python 3.12+ |
| **Framework** | FastAPI (async) |
| **Database** | PostgreSQL 15+ with `ltree` extension |

---

## 2. Technology Stack Rules

### Backend
- **Python 3.12+** — use modern syntax (match statements, `type` keyword where appropriate).
- **FastAPI** — async route handlers; use `Depends` for dependency injection; never use global mutable state.
- **Pydantic v2** — strict mode for all request/response models; use `model_validator` for cross-field validation.
- **SQLAlchemy 2.0** — use the 2.0-style `select()` API, not the legacy `Query` API; async session via `asyncpg`.
- **Alembic** — all schema changes via migrations; never modify the DB manually.
- **Celery** with Redis broker — for async jobs (aggregation sync, reminders, key rotation).
- **httpx** — for all external HTTP calls (Open Banking APIs); always use async client.

### Database
- PostgreSQL 15+ with `ltree` extension enabled.
- Use `Numeric(19,4)` for all monetary columns — never `float` or `double`.
- UUIDs v4 for all primary keys — use `uuid_generate_v4()` default.
- Timestamps always `timestamptz` in UTC.

### Testing
- **pytest** + **pytest-asyncio** — async test support.
- **Hypothesis** — property-based testing for monetary calculations and categorisation logic.
- **Factory Boy** — test fixtures; do not use raw SQL inserts in tests.
- Coverage target: ≥ 85% line coverage.

### Infrastructure
- Docker Compose for local development.
- GitHub Actions for CI/CD.
- Redis 7+ for caching and rate limiting.

---

## 3. Domain Rules — Banking & Finance

### Monetary Values
- **ALWAYS** use `Decimal` (Python `decimal.Decimal`) for monetary arithmetic.
- **NEVER** use `float` or `round()` on money — use `Decimal.quantize()` with `ROUND_HALF_EVEN` (banker's rounding).
- Store amounts with 4 decimal places in the database; display with currency-specific minor units (2 for EUR/USD, 0 for JPY).
- Currency codes must conform to ISO 4217; validate on input.

### Account & Transaction Integrity
- Every balance change must be traceable to a transaction.
- Transactions are immutable after creation — corrections are new offsetting transactions, never updates.
- Soft-delete for accounts; hard-delete only via GDPR erasure.

### Multi-Currency
- Store both original and converted amounts on every transaction.
- Exchange rates sourced from ECB daily feed; cached in Redis with 24h TTL.
- Net-worth and reporting aggregations convert to user's base currency.

### Categorisation
- System categories are read-only for users; users create custom categories.
- Auto-categorisation priority: user override (transaction-level) > user override (code-level) > MCC mapping > "Uncategorised".
- Overrides stored with original category for ML training data.

---

## 4. Code Style & Conventions

### Naming
- **Files**: `snake_case.py` (e.g., `auto_categoriser.py`).
- **Classes**: `PascalCase` (e.g., `AutoCategoriser`, `PFMAccount`).
- **Functions/methods**: `snake_case` (e.g., `categorise_transaction`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_CATEGORY_DEPTH`).
- **API paths**: `kebab-case` (e.g., `/pfm/spending-summary`).
- **Database tables**: `snake_case` with `pfm_` prefix (e.g., `pfm_transactions`, `pfm_categories`).

### Architecture
- **Layered architecture**: `api/` (routers) → `services/` (business logic) → `models/` (data access).
- Routers must not contain business logic — delegate to service classes.
- Services receive dependencies via constructor injection; must be testable without a running database.
- One file per model; one file per router; services may span a feature folder.

### Type Annotations
- All functions must have complete type annotations (parameters and return types).
- Use `from __future__ import annotations` for forward references.
- Prefer `list[str]` over `List[str]` (modern syntax).

### Docstrings
- All public classes and functions require docstrings.
- Use Google-style docstrings.
- Include `Args`, `Returns`, `Raises` sections where applicable.

### Error Handling
- Use custom exception classes inheriting from a `PFMBaseError`.
- Map exceptions to RFC 7807 Problem Details in a central error handler.
- Never catch bare `Exception` — catch specific exceptions.
- Log exceptions at ERROR level with stack trace; never expose traces in API responses.

### Imports
- Standard library → third-party → local imports, separated by blank lines.
- Use absolute imports within the `pfm` package.
- No wildcard imports (`from x import *`).

---

## 5. Security Constraints

### Authentication & Authorisation
- All endpoints require a valid JWT from the banking platform's auth service.
- User can only access their own data — enforce `user_id` filtering in every query.
- Compliance endpoints (erasure, export) require SCA step-up re-authentication.
- Admin/ops endpoints (if any) require a separate `ops-admin` role.

### Data Protection
- **PAN (Primary Account Number)**: never store full PAN; use tokenisation. Display masked to last 4 digits.
- **Custom notes and tags**: encrypted at rest with AES-256-GCM; decrypted only at the service layer, never in the DB query.
- **Logs**: scan for and mask any PAN-like patterns before writing; never log access tokens, session IDs, or plaintext secrets.

### Input Validation
- Validate all inputs via Pydantic strict models before any business logic.
- Sanitise all user-supplied text (strip HTML/JS) using `bleach` or equivalent.
- Reject any input exceeding reasonable length limits (e.g., notes ≤ 500 chars, category name ≤ 255 chars).

### Dependencies
- Pin all dependency versions in `requirements.txt` / `pyproject.toml`.
- Run `pip-audit` in CI to check for known vulnerabilities.
- No use of `eval()`, `exec()`, `pickle.loads()`, or `subprocess.shell=True`.

---

## 6. Compliance Constraints

### PSD2 (Payment Services Directive 2)
- Aggregation of external accounts requires explicit user consent with defined scope and expiry.
- Implement SCA (Strong Customer Authentication) for consent creation and sensitive operations.
- Consent tokens must be stored securely and revocable by the user at any time.
- Log all consent lifecycle events (created, used, revoked, expired).

### GDPR (General Data Protection Regulation)
- Provide data export (Article 20 — portability) in machine-readable JSON.
- Provide data erasure (Article 17 — right to be forgotten) with cascade across all PFM tables.
- Anonymise (not delete) audit log entries upon erasure — retain action and timestamp, hash the user_id.
- Document all personal data processing activities.

### PCI DSS (Payment Card Industry Data Security Standard)
- Never store full PAN, CVV, or PIN in any PFM table or log.
- Encrypt cardholder data in transit (TLS 1.2+) and at rest (AES-256-GCM).
- Implement key management with KEK/DEK separation; support key rotation without downtime.
- Restrict database access to the application service account; no ad-hoc query access in production.

---

## 7. Testing Expectations

### What to Test
- **Unit tests**: every public method in service classes; edge cases for monetary calculations; categorisation priority logic.
- **Integration tests**: full request-response cycle via TestClient; database state assertions; audit log verification.
- **Property-based tests**: monetary arithmetic properties (associativity, commutativity of conversions, no precision loss).
- **Compliance tests**: GDPR erasure completeness; PCI masking correctness; PSD2 consent lifecycle.

### How to Test
- Use Factory Boy for fixtures — never hardcode test data inline.
- Each integration test runs in a DB transaction that is rolled back after the test.
- Mock external services (Open Banking APIs) with `respx` or `httpx` mock transport.
- CI must run full test suite; merge blocked if coverage drops below 85% or any test fails.

### What NOT to Do in Tests
- Do not test framework internals (FastAPI routing, Pydantic validation) — trust the framework.
- Do not write tests that depend on execution order.
- Do not use `sleep()` or time-based assertions — use frozen time (`freezegun`).

---

## 8. Agent Behaviour Guidelines

### When Generating Code
1. Always read the relevant specification task before writing code.
2. Check existing code in the target file/folder before creating new files.
3. Follow the layered architecture: never put business logic in routers.
4. Add type annotations and docstrings to every new public function.
5. Create or update unit tests alongside implementation — never leave tests for later.

### When Reviewing Code
1. Check for floating-point usage on monetary values — flag immediately.
2. Verify that user data access is scoped by `user_id`.
3. Confirm audit events are emitted for state-changing operations.
4. Verify sensitive fields are encrypted/masked in responses and logs.
5. Check that new endpoints are documented in OpenAPI.

### When Debugging
1. Check the audit log first — it provides a history of all state changes.
2. Use correlation IDs to trace requests across services.
3. Never access production data directly — use the GDPR export endpoint for user data inspection.

### Things to NEVER Do
- Never use `float` for money.
- Never log sensitive data (PANs, tokens, passwords, full user data).
- Never skip input validation.
- Never hardcode secrets — always use environment variables.
- Never bypass SCA for compliance-sensitive operations.
- Never delete audit log entries.
- Never use `SELECT *` in production queries.
- Never commit `.env` files or secrets to version control.
