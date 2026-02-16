# Claude Code Rules — PFM Module

> These rules steer Claude Code (and similar AI assistants) when working inside the `pfm/` directory of the banking monorepo.

## Project Context

This is a **Personal Financial Management (PFM)** module embedded in an existing internal banking platform. The module handles sensitive financial data in a regulated environment (PSD2, GDPR, PCI DSS).

Read `specification.md` for the full feature spec. Read `agents.md` for tech stack and domain rules.

---

## Mandatory Rules

### 1. Money is Decimal — No Exceptions
- Use `decimal.Decimal` for ALL monetary values in Python.
- Use `Numeric(19,4)` in PostgreSQL.
- Use `Decimal.quantize()` with `ROUND_HALF_EVEN` for display rounding.
- NEVER use `float`, `round()`, or integer-cents patterns for money.

### 2. User Data Isolation
- Every database query that touches user data MUST filter by `user_id`.
- Never return data belonging to a different user.
- If a query is missing a `user_id` filter, add one before proceeding.

### 3. Audit Everything
- Every state-changing operation (create, update, delete) MUST emit an audit event via `AuditLogger`.
- Audit events include: `actor, action, resource_type, resource_id, before_state, after_state, correlation_id, timestamp`.
- Never skip audit logging, even in error paths.

### 4. Encrypt Sensitive Fields
- `Transaction.custom_notes` and `Transaction.custom_tags` are encrypted at rest.
- Never query or filter on encrypted fields directly in SQL — decrypt in the service layer.
- Never log decrypted sensitive field values.

### 5. Mask Card Data
- Never include full PAN in any API response, log, or error message.
- Use `PCIMasker.mask_pan()` before any PAN leaves the service layer.
- If you see a PAN pattern in a log statement, mask it immediately.

### 6. Sanitise User Input
- All user-supplied text (notes, tags, category names, descriptions) MUST be sanitised.
- Strip HTML, JavaScript, and control characters before storage.
- Enforce length limits: notes ≤ 500 chars, category name ≤ 255 chars.

---

## Code Patterns to Follow

### File Structure
```
pfm/
├── api/           # FastAPI routers only — no business logic here
├── services/      # Business logic — testable without DB
├── models/        # SQLAlchemy + Pydantic models
├── aggregation/   # Open Banking adapters + manual entry
├── categorisation/ # Category tree + auto-categoriser
├── projections/   # Templates, engine, reminders
├── compliance/    # GDPR, PCI, audit, encryption
├── i18n/          # Locale files
├── tests/         # Unit + integration tests
└── migrations/    # Alembic
```

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- DB tables: `pfm_` prefix, `snake_case`
- API paths: `kebab-case` under `/pfm/`

### Import Order
```python
# 1. Standard library
from decimal import Decimal
from uuid import UUID

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select

# 3. Local
from pfm.models.account import PFMAccount
from pfm.services.category_service import CategoryService
```

### Error Pattern
```python
# Define custom exceptions in pfm/exceptions.py
class PFMBaseError(Exception): ...
class AccountNotFoundError(PFMBaseError): ...
class InsufficientPermissionError(PFMBaseError): ...

# Map to RFC 7807 in a central handler — not in individual routes
```

### Testing Pattern
```python
# Use Factory Boy, not raw inserts
# Use freezegun for time-dependent tests
# One assertion focus per test
# Mock external APIs with respx
```

---

## Things to AVOID

- **Do NOT** put business logic in API routers — delegate to service classes.
- **Do NOT** use `SELECT *` — always specify columns.
- **Do NOT** use `from x import *` — explicit imports only.
- **Do NOT** use `eval()`, `exec()`, `pickle.loads()`, or `subprocess` with `shell=True`.
- **Do NOT** catch bare `Exception` — catch specific exception types.
- **Do NOT** hardcode secrets, API keys, or database URLs — use env vars.
- **Do NOT** commit `.env` files or test credentials.
- **Do NOT** create new files outside the `pfm/` directory without explicit instruction.
- **Do NOT** modify `core-banking/` code without explicit approval.
- **Do NOT** skip writing tests when implementing a new feature.
- **Do NOT** use `time.sleep()` in tests — use `freezegun` or async test patterns.

---

## When You're Unsure

1. Check `specification.md` for feature requirements and task details.
2. Check `agents.md` for domain rules and tech stack guidance.
3. Look at existing code in `pfm/` for established patterns.
4. If something conflicts with compliance rules (PSD2/GDPR/PCI DSS), the compliance rule wins.
5. Ask for clarification rather than guessing on security-sensitive decisions.

---

## Commit Messages

Use conventional commit format:
```
feat(pfm): add category tree CRUD endpoints
fix(pfm): correct decimal rounding in currency conversion
test(pfm): add integration tests for GDPR erasure
docs(pfm): update OpenAPI descriptions for aggregation endpoints
```
