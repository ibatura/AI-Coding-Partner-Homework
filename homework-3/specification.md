# Personal Financial Management Module — Specification

> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## High-Level Objective

- Build a **Personal Financial Management (PFM)** module that integrates into the existing internal banking system, giving customers a unified view of their finances — internal and external accounts, hierarchical spending categories, scheduled projections, and compliance-ready reporting — while meeting PSD2, GDPR, and PCI DSS requirements.

## Mid-Level Objectives

1. **Account & Multi-Currency Foundation** — Create bank accounts per user with multi-currency support (EUR, USD, GBP, and others via ISO 4217), store balances using precise decimal arithmetic, and localise the UI/API responses into multiple languages (EN, DE, FR minimum) via i18n.
2. **Account Aggregation** — Allow users to link external financial accounts (credit cards, loans, other banks) through Open Banking / PSD2-compliant APIs (AISP access) and manual entry; normalise all transactions into a canonical internal model with currency conversion.
3. **Hierarchical Categorisation Engine** — Implement an arbitrarily nested category tree (parent-child, unlimited depth) with automatic MCC/transaction-code-based categorisation and user overrides; store overrides as labelled training data for future ML models.
4. **Scheduled Spending Projections** — Enable recurring expense templates and income entries; project future balances on a calendar; generate reminders via configurable notification channels.
5. **Compliance & Reporting** — Enforce PSD2 consent management for aggregated data, GDPR right-to-erasure on request, PCI DSS encryption of cardholder data in transit and at rest, and produce financial reports in JSON format with full audit trails.
6. **Category Overrides & Custom Data Injection** — Let users override automatic categorisation per transaction or per transaction code, attach sanitised/encrypted custom metadata (notes, tags), and expose override data for ML training pipelines.

## Implementation Notes

### Technical Constraints
- All monetary values **MUST** use `Decimal` (or language-equivalent fixed-point) — never floating-point.
- Timestamps **MUST** be stored as UTC `ISO 8601` with timezone offset retained for display.
- Database IDs **MUST** be UUIDs v4.
- The module integrates into the existing banking system's authentication and authorisation (OAuth 2.0 / OpenID Connect); do not build a standalone auth layer.
- API design follows **REST** principles with OpenAPI 3.1 documentation auto-generated from code.
- All endpoints require **TLS 1.2+** in transit; sensitive fields (PAN, notes) are encrypted at rest with AES-256-GCM.

### Technology Stack (recommended)
| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.12+ / FastAPI |
| Database | PostgreSQL 15+ with `ltree` extension for category hierarchy |
| Caching | Redis 7+ |
| Task Queue | Celery with Redis broker |
| External Aggregation | Open Banking UK / Berlin Group NextGenPSD2 API adapters |
| Localisation | GNU gettext / `babel` |
| Testing | pytest, pytest-asyncio, Hypothesis (property-based) |
| CI/CD | GitHub Actions |

### Performance Requirements
- P95 latency ≤ 200 ms for single-account transaction listing (paginated, 50 items).
- Category tree queries optimised via PostgreSQL `ltree` index; recursive CTE fallback with materialised path caching.
- Aggregation sync must run asynchronously and not block the user session.

### Security & Compliance
- **PSD2**: Implement Strong Customer Authentication (SCA) for aggregation consent; store consent tokens with expiry; revoke on user request.
- **GDPR**: Provide `/users/{id}/data-export` and `/users/{id}/data-erasure` endpoints. Erasure must cascade to aggregated data, overrides, notes, and projection templates. Log erasure events in an immutable audit log.
- **PCI DSS**: Never log full card numbers; mask to last four digits in all API responses and logs; use tokenisation for stored PANs.
- All user-supplied text (notes, tags, category names) **MUST** be sanitised (strip HTML/JS) before storage and encrypted at rest.

### Audit & Logging
- Every state-changing operation emits an immutable audit event: `{ actor, action, resource, timestamp, before, after }`.
- Audit log stored in an append-only table; retention ≥ 7 years (configurable per regulatory jurisdiction).
- Structured logging (JSON) to stdout; correlation IDs propagated across service boundaries.

### Error Handling
- Use RFC 7807 Problem Details for all error responses.
- Distinguish between client errors (4xx) and server errors (5xx) with actionable `detail` messages.
- Never expose stack traces or internal identifiers in production error responses.

### Input Validation
- All request bodies validated via Pydantic v2 models with strict mode enabled.
- Currency codes validated against ISO 4217.
- Transaction amounts validated as positive decimals with max 2 decimal places (or currency-specific minor units).

---

## Context

### Beginning Context

- **Existing system**: Internal banking platform with user management, core account ledger, and authentication (OAuth 2.0 / OIDC).
- **Existing files/services**:
  - `core-banking/accounts/` — account creation, balance queries (internal accounts only).
  - `core-banking/auth/` — OAuth 2.0 provider, user identity.
  - `core-banking/common/` — shared utilities, logging, base models.
  - `infra/docker-compose.yml` — PostgreSQL, Redis, API gateway.
- **No PFM module exists** — this is a greenfield addition within the established monorepo.
- **Available**: PostgreSQL `ltree` extension, Redis, Celery worker pool, CI/CD pipeline.

### Ending Context

- **New files/services** (all under `pfm/`):
  - `pfm/api/` — FastAPI routers for each feature area.
  - `pfm/models/` — SQLAlchemy / Pydantic models.
  - `pfm/services/` — business logic layer.
  - `pfm/aggregation/` — Open Banking adapters and manual-entry service.
  - `pfm/categorisation/` — category tree CRUD, auto-categoriser, override store.
  - `pfm/projections/` — recurring template engine, calendar projection, reminders.
  - `pfm/compliance/` — consent management, GDPR erasure, audit logger.
  - `pfm/i18n/` — locale files (EN, DE, FR+).
  - `pfm/tests/` — unit, integration, and compliance test suites.
  - `docs/openapi.yaml` — generated OpenAPI spec.
  - `docs/data-model.md` — ERD and data dictionary.
- **Updated files**:
  - `infra/docker-compose.yml` — add `ltree` init script, Celery workers.
  - `core-banking/common/` — shared audit-event emitter.
- **Deliverables**: All endpoints documented, test coverage ≥ 85 %, audit log operational, GDPR erasure verified by integration test.

---

## Low-Level Tasks

### 1. Database Schema — Accounts & Multi-Currency

**What prompt would you run to complete this task?**
Create the SQLAlchemy models and Alembic migration for PFM accounts, supporting multi-currency balances with Decimal precision. Each user can have multiple accounts. Store currency as ISO 4217 code. Include created_at, updated_at, and soft-delete flag.

**What file do you want to CREATE or UPDATE?**
`pfm/models/account.py`, `pfm/migrations/versions/001_create_pfm_accounts.py`

**What function do you want to CREATE or UPDATE?**
`class PFMAccount(Base)`, `class AccountBalance(Base)`

**What are details you want to add to drive the code changes?**
- `PFMAccount`: id (UUID PK), user_id (FK to core user), name, account_type ENUM (checking, savings, credit, loan, external), currency_code (char 3), is_external (bool), provider (nullable str for Open Banking), created_at, updated_at, deleted_at (nullable).
- `AccountBalance`: id (UUID PK), account_id (FK), balance (Numeric 19,4), as_of_date (timestamptz).
- Add composite index on (user_id, deleted_at) for fast active-account lookups.
- Validate currency_code against ISO 4217 set in a Pydantic validator.

---

### 2. Database Schema — Transaction Model

**What prompt would you run to complete this task?**
Create the canonical transaction model that normalises internal banking transactions and externally aggregated ones. Include fields for categorisation, custom metadata, and audit.

**What file do you want to CREATE or UPDATE?**
`pfm/models/transaction.py`, `pfm/migrations/versions/002_create_transactions.py`

**What function do you want to CREATE or UPDATE?**
`class Transaction(Base)`

**What are details you want to add to drive the code changes?**
- id (UUID PK), account_id (FK), amount (Numeric 19,4), currency_code, original_amount (Numeric, for multi-currency conversion), original_currency_code, exchange_rate (Numeric 12,6).
- transaction_date (timestamptz), booking_date (timestamptz), value_date (timestamptz).
- mcc_code (char 4, nullable), transaction_code (varchar), description (text).
- category_id (FK, nullable), is_category_overridden (bool, default false).
- custom_notes (text, encrypted at rest), custom_tags (JSONB, encrypted at rest).
- source ENUM (internal, open_banking, manual).
- created_at, updated_at.
- Index on (account_id, transaction_date DESC) for paginated listing.
- GIN index on custom_tags for tag-based queries.

---

### 3. Database Schema — Category Hierarchy (ltree)

**What prompt would you run to complete this task?**
Create the hierarchical category model using PostgreSQL ltree. Support system-default categories and user-custom categories. Include materialised path for efficient tree queries.

**What file do you want to CREATE or UPDATE?**
`pfm/models/category.py`, `pfm/migrations/versions/003_create_categories.py`

**What function do you want to CREATE or UPDATE?**
`class Category(Base)`, `class CategoryOverride(Base)`

**What are details you want to add to drive the code changes?**
- `Category`: id (UUID PK), user_id (FK, nullable — null = system default), name (varchar 255), path (LtreeType), parent_id (FK self, nullable), icon (varchar), is_system (bool), created_at, updated_at.
- `CategoryOverride`: id (UUID PK), user_id (FK), transaction_id (FK, nullable — per-transaction), transaction_code (varchar, nullable — per-code), original_category_id (FK), override_category_id (FK), created_at.
  - Constraint: at least one of transaction_id or transaction_code must be non-null.
- GiST index on `path` column for ltree ancestor/descendant queries.
- Seed migration inserts default category tree (e.g., Housing > Rent, Housing > Mortgage, Food > Groceries, Food > Restaurants, Transport > Fuel, etc.).
- Override records include `original_category_id` to serve as ML training pairs.

---

### 4. Account Aggregation — Open Banking Adapter

**What prompt would you run to complete this task?**
Implement the Open Banking (PSD2 AISP) adapter layer. Create an abstract adapter interface and a concrete implementation for the Berlin Group NextGenPSD2 sandbox. Handle consent creation, token storage, account listing, and transaction fetching.

**What file do you want to CREATE or UPDATE?**
`pfm/aggregation/adapter_base.py`, `pfm/aggregation/nextgen_psd2.py`, `pfm/aggregation/consent.py`

**What function do you want to CREATE or UPDATE?**
`class AggregationAdapter(ABC)`, `class NextGenPSD2Adapter(AggregationAdapter)`, `class ConsentService`

**What are details you want to add to drive the code changes?**
- `AggregationAdapter` abstract methods: `create_consent()`, `get_accounts()`, `get_transactions(account_id, date_from, date_to)`, `revoke_consent()`.
- `NextGenPSD2Adapter`: HTTP client (httpx async), retries with exponential backoff, map external transaction fields to canonical `Transaction` model.
- `ConsentService`: store consent token, ASPSP ID, scope, expiry, and SCA redirect URL in `pfm/models/consent.py`. Auto-revoke expired consents via Celery beat task.
- Never log access tokens; mask in debug logs.
- All external HTTP calls go through the API gateway with mTLS.

---

### 5. Account Aggregation — Manual Entry Service

**What prompt would you run to complete this task?**
Create a service for users to manually add external accounts and transactions when Open Banking is unavailable. Validate and normalise manual entries to the same canonical model.

**What file do you want to CREATE or UPDATE?**
`pfm/aggregation/manual_entry.py`, `pfm/api/aggregation.py`

**What function do you want to CREATE or UPDATE?**
`class ManualEntryService`, `router` (FastAPI APIRouter)

**What are details you want to add to drive the code changes?**
- `ManualEntryService.add_account(user_id, name, currency, account_type)` — creates `PFMAccount(is_external=True, source='manual')`.
- `ManualEntryService.add_transaction(account_id, amount, currency, date, description, category_id=None)` — validates amount > 0, currency is ISO 4217, date is not in the future beyond 1 day tolerance.
- API endpoints: `POST /pfm/aggregation/manual/accounts`, `POST /pfm/aggregation/manual/transactions`.
- Input sanitisation: strip HTML from description, enforce max length 500 chars.
- Emit audit event for every manual entry.

---

### 6. Categorisation Engine — Auto-Categoriser

**What prompt would you run to complete this task?**
Implement the automatic categorisation service that maps MCC codes and transaction codes to categories. Apply user overrides before falling back to system defaults.

**What file do you want to CREATE or UPDATE?**
`pfm/categorisation/auto_categoriser.py`, `pfm/models/mcc_mapping.py`

**What function do you want to CREATE or UPDATE?**
`class AutoCategoriser`, `class MCCMapping(Base)`

**What are details you want to add to drive the code changes?**
- `MCCMapping`: mcc_code (PK char 4), category_id (FK), description.
- `AutoCategoriser.categorise(transaction)`:
  1. Check `CategoryOverride` for matching transaction_id.
  2. Check `CategoryOverride` for matching transaction_code + user_id.
  3. Look up `MCCMapping` by mcc_code.
  4. If no match, assign "Uncategorised" system category.
  5. Set `transaction.is_category_overridden = True` if step 1 or 2 matched.
- Batch categorisation: accept list of transactions, process with a single DB round-trip for override lookups.
- Log categorisation decisions at DEBUG level with correlation ID.

---

### 7. Categorisation — Category CRUD & Tree Operations

**What prompt would you run to complete this task?**
Create API endpoints for managing the category hierarchy: list tree, create custom category, rename, move (re-parent), delete (with orphan handling), and get spending totals per subtree.

**What file do you want to CREATE or UPDATE?**
`pfm/api/categories.py`, `pfm/services/category_service.py`

**What function do you want to CREATE or UPDATE?**
`class CategoryService`, `router` (FastAPI APIRouter)

**What are details you want to add to drive the code changes?**
- `GET /pfm/categories` — return full tree for user (system + custom), using `ltree` `@>` operator for subtree queries.
- `POST /pfm/categories` — create custom category under a parent; update ltree path = parent.path + slugified name.
- `PATCH /pfm/categories/{id}` — rename or re-parent; re-parent must update ltree paths of all descendants in one query (`UPDATE ... SET path = new_prefix || subpath(path, nlevel(old_prefix))`).
- `DELETE /pfm/categories/{id}` — reassign child categories to parent before deleting; disallow deleting system categories.
- `GET /pfm/categories/{id}/totals?from=&to=` — aggregate transaction amounts for the category and all descendants using ltree descendant query, with optional currency conversion.
- Optimise recursive queries: use materialised path via ltree index, fall back to recursive CTE only for ad-hoc deep aggregations.

---

### 8. Scheduled Projections — Recurring Templates

**What prompt would you run to complete this task?**
Create the recurring expense/income template model and the projection engine that generates future transactions on a calendar.

**What file do you want to CREATE or UPDATE?**
`pfm/models/projection.py`, `pfm/projections/engine.py`, `pfm/projections/scheduler.py`

**What function do you want to CREATE or UPDATE?**
`class RecurringTemplate(Base)`, `class ProjectionEngine`, `class ProjectionScheduler`

**What are details you want to add to drive the code changes?**
- `RecurringTemplate`: id (UUID), user_id (FK), name, amount (Numeric 19,4), currency_code, category_id (FK), frequency ENUM (daily, weekly, biweekly, monthly, quarterly, yearly), start_date, end_date (nullable), next_occurrence, is_income (bool), is_active (bool), created_at, updated_at.
- `ProjectionEngine.project(user_id, horizon_months=6)`:
  1. Fetch all active templates for user.
  2. Generate projected entries from `next_occurrence` to horizon.
  3. Return list of `{ date, amount, currency, category, template_name, is_income }`.
  4. Aggregate by month for summary view.
- `ProjectionScheduler` (Celery beat): daily task to update `next_occurrence` after each real date passes; emit reminder notifications N days before (configurable per template).
- API endpoints: `POST/GET/PATCH/DELETE /pfm/projections/templates`, `GET /pfm/projections/calendar?from=&to=`.

---

### 9. Scheduled Projections — Reminders

**What prompt would you run to complete this task?**
Implement the reminder system for upcoming projected expenses/income. Integrate with the banking platform's notification service.

**What file do you want to CREATE or UPDATE?**
`pfm/projections/reminders.py`, `pfm/api/projections.py`

**What function do you want to CREATE or UPDATE?**
`class ReminderService`, `router` (FastAPI APIRouter)

**What are details you want to add to drive the code changes?**
- `ReminderService.check_and_send(user_id)`: query templates where `next_occurrence - today <= remind_days_before`; call existing banking notification service (push, email, SMS) via internal message bus.
- User preferences: `remind_days_before` (int, default 3), `reminder_channels` (list of enum: push, email, sms).
- Store reminder history: `ReminderLog(id, user_id, template_id, sent_at, channel, status)`.
- Celery beat task runs daily at 08:00 UTC; respect user timezone for delivery window.
- API: `GET /pfm/projections/reminders` — list upcoming reminders, `PATCH /pfm/projections/templates/{id}/reminder` — update reminder preferences.

---

### 10. Compliance — GDPR Erasure & Data Export

**What prompt would you run to complete this task?**
Implement GDPR right-to-erasure and data-portability endpoints. Erasure must cascade across all PFM data. Export must produce a machine-readable JSON archive.

**What file do you want to CREATE or UPDATE?**
`pfm/compliance/gdpr.py`, `pfm/api/compliance.py`

**What function do you want to CREATE or UPDATE?**
`class GDPRErasureService`, `class GDPRExportService`, `router` (FastAPI APIRouter)

**What are details you want to add to drive the code changes?**
- `GDPRErasureService.erase(user_id)`:
  1. Delete (hard delete) all: transactions, accounts, categories (custom), overrides, projection templates, reminder logs, consents, custom notes/tags.
  2. Retain anonymised audit log entries (replace user_id with hash, keep action and timestamp).
  3. Write immutable erasure confirmation event to audit log.
  4. Return confirmation receipt with erasure timestamp.
- `GDPRExportService.export(user_id)`:
  1. Gather all user data across PFM tables.
  2. Serialise to JSON using canonical schemas.
  3. Return as downloadable `.json` file (streamed for large datasets).
- Endpoints: `POST /pfm/compliance/erasure`, `GET /pfm/compliance/export` — both require re-authentication (SCA step-up).
- Integration test: create user data, call erasure, verify zero rows remain (except anonymised audit).

---

### 11. Compliance — PCI DSS & Encryption

**What prompt would you run to complete this task?**
Implement field-level encryption for sensitive data (card numbers, custom notes, tags) and PCI DSS-compliant masking in API responses.

**What file do you want to CREATE or UPDATE?**
`pfm/compliance/encryption.py`, `pfm/compliance/masking.py`

**What function do you want to CREATE or UPDATE?**
`class FieldEncryptor`, `class PCIMasker`

**What are details you want to add to drive the code changes?**
- `FieldEncryptor`: use AES-256-GCM via `cryptography` library; key management via environment-injected KEK (key-encryption-key) with per-field DEKs (data-encryption-keys) stored in a key table.
  - `encrypt(plaintext) -> (ciphertext, iv, tag)`
  - `decrypt(ciphertext, iv, tag) -> plaintext`
- Apply to: `Transaction.custom_notes`, `Transaction.custom_tags`, any stored PAN fragments.
- `PCIMasker.mask_pan(pan) -> str`: return `"**** **** **** " + pan[-4:]`.
- Pydantic response models must call `PCIMasker` in serialisers — never return raw PANs.
- Logging middleware: scan log payloads for PAN patterns (`\b\d{13,19}\b`) and mask before writing.
- Key rotation: support re-encrypting fields with new DEK via async Celery task.

---

### 12. Compliance — Audit Logging

**What prompt would you run to complete this task?**
Create the immutable audit logging system that records every state-changing operation across the PFM module.

**What file do you want to CREATE or UPDATE?**
`pfm/compliance/audit.py`, `pfm/models/audit.py`

**What function do you want to CREATE or UPDATE?**
`class AuditLogger`, `class AuditEvent(Base)`

**What are details you want to add to drive the code changes?**
- `AuditEvent`: id (UUID), actor_id (UUID), actor_type ENUM (user, system, admin), action (varchar 100), resource_type (varchar 100), resource_id (UUID), before_state (JSONB, nullable), after_state (JSONB, nullable), correlation_id (UUID), ip_address (inet), timestamp (timestamptz, default now()).
- Table is append-only: no UPDATE or DELETE permissions granted to the application role; enforced via PostgreSQL row-level security or a separate audit schema with restricted privileges.
- `AuditLogger` is a FastAPI dependency injected into route handlers; exposes `log(action, resource_type, resource_id, before, after)`.
- Middleware to auto-inject `correlation_id` and `ip_address` from request context.
- Retention policy: configurable via env var, default 7 years; archival to cold storage via Celery periodic task.

---

### 13. Internationalisation (i18n) & Localisation

**What prompt would you run to complete this task?**
Add multi-language support to all API responses, error messages, and category names. Use GNU gettext with Babel for extraction and compilation.

**What file do you want to CREATE or UPDATE?**
`pfm/i18n/setup.py`, `pfm/i18n/locales/en/LC_MESSAGES/messages.po`, `pfm/i18n/locales/de/LC_MESSAGES/messages.po`, `pfm/i18n/locales/fr/LC_MESSAGES/messages.po`

**What function do you want to CREATE or UPDATE?**
`get_locale()`, `translate()` (helper), FastAPI middleware for locale detection

**What are details you want to add to drive the code changes?**
- Detect locale from `Accept-Language` header; fall back to user profile preference; ultimate fallback `en`.
- Mark all user-facing strings with `_()` for extraction.
- System category names stored in default locale (EN); translations provided via `.po` files, loaded at startup.
- Error messages (RFC 7807 `title` and `detail`) are translated.
- Currency formatting respects locale (e.g., `1.234,56 EUR` for DE vs `EUR 1,234.56` for EN).
- Date formatting respects locale via `babel.dates`.

---

### 14. API Layer — Routers, Middleware & OpenAPI Docs

**What prompt would you run to complete this task?**
Wire all service modules into FastAPI routers, add shared middleware (auth, correlation ID, rate limiting, locale), and generate OpenAPI 3.1 documentation.

**What file do you want to CREATE or UPDATE?**
`pfm/api/app.py`, `pfm/api/middleware.py`, `pfm/api/deps.py`

**What function do you want to CREATE or UPDATE?**
`create_app()`, `AuthMiddleware`, `CorrelationMiddleware`, `RateLimitMiddleware`, `get_current_user()`

**What are details you want to add to drive the code changes?**
- `create_app()`: initialise FastAPI with `title="PFM Module"`, include all routers under `/pfm` prefix, add middleware stack.
- `AuthMiddleware`: validate JWT from existing banking auth service; extract user_id and roles; reject with 401 if invalid.
- `CorrelationMiddleware`: read `X-Correlation-ID` header or generate UUID; attach to request state; propagate to all outgoing calls and logs.
- `RateLimitMiddleware`: per-user rate limiting via Redis sliding window; 100 req/min default; 10 req/min for compliance endpoints.
- `get_current_user()`: FastAPI `Depends` that returns authenticated user context.
- Auto-generate OpenAPI spec; serve Swagger UI at `/pfm/docs` (disabled in production).
- Health check: `GET /pfm/health` — verify DB and Redis connectivity.

---

### 15. Testing — Unit Tests

**What prompt would you run to complete this task?**
Create comprehensive unit tests for all service classes: AutoCategoriser, ProjectionEngine, FieldEncryptor, PCIMasker, GDPRErasureService, ManualEntryService. Use pytest with fixtures and Hypothesis for property-based tests on monetary calculations.

**What file do you want to CREATE or UPDATE?**
`pfm/tests/unit/test_categoriser.py`, `pfm/tests/unit/test_projections.py`, `pfm/tests/unit/test_encryption.py`, `pfm/tests/unit/test_gdpr.py`, `pfm/tests/unit/test_manual_entry.py`

**What function do you want to CREATE or UPDATE?**
Test functions for each service method

**What are details you want to add to drive the code changes?**
- `test_categoriser.py`: test override priority (transaction > code > MCC > uncategorised); test batch categorisation; test with unknown MCC code.
- `test_projections.py`: test monthly/weekly/yearly frequency generation; test horizon boundary; test inactive template skipped; Hypothesis: `amount * n_occurrences` never loses precision.
- `test_encryption.py`: round-trip encrypt/decrypt; test with empty string; test key rotation re-encrypt.
- `test_gdpr.py`: mock DB, verify all tables touched by erasure; verify audit log anonymised but retained.
- `test_manual_entry.py`: valid entry; reject future date > 1 day; reject negative amount; reject invalid currency.
- Target: ≥ 85 % line coverage across `pfm/services/` and `pfm/compliance/`.

---

### 16. Testing — Integration Tests

**What prompt would you run to complete this task?**
Create integration tests that exercise the full request-response cycle through FastAPI's TestClient with a real PostgreSQL test database. Cover account creation, aggregation, categorisation, projections, and compliance flows.

**What file do you want to CREATE or UPDATE?**
`pfm/tests/integration/test_accounts_api.py`, `pfm/tests/integration/test_aggregation_api.py`, `pfm/tests/integration/test_categories_api.py`, `pfm/tests/integration/test_projections_api.py`, `pfm/tests/integration/test_compliance_api.py`

**What function do you want to CREATE or UPDATE?**
Integration test functions per API flow

**What are details you want to add to drive the code changes?**
- Use `pytest-asyncio` and FastAPI `TestClient` with test DB (Alembic migrations applied in fixture).
- `test_accounts_api.py`: create account, list accounts, verify multi-currency.
- `test_aggregation_api.py`: mock Open Banking adapter; verify transactions normalised and categorised.
- `test_categories_api.py`: create custom subcategory, move it, delete parent (verify orphan reassignment), query subtree totals.
- `test_projections_api.py`: create template, fetch calendar, verify projected amounts and dates.
- `test_compliance_api.py`: create full user dataset, trigger erasure, verify zero PFM rows, verify anonymised audit log remains; test export returns valid JSON with all user data.
- Separate test DB per run; teardown via transaction rollback.

---

### 17. Reporting — JSON Financial Reports

**What prompt would you run to complete this task?**
Implement financial reporting endpoints that generate spending summaries, category breakdowns, and net-worth snapshots in JSON format.

**What file do you want to CREATE or UPDATE?**
`pfm/services/reporting.py`, `pfm/api/reports.py`

**What function do you want to CREATE or UPDATE?**
`class ReportingService`, `router` (FastAPI APIRouter)

**What are details you want to add to drive the code changes?**
- `GET /pfm/reports/spending-summary?from=&to=&currency=` — total spending, total income, net, grouped by month.
- `GET /pfm/reports/category-breakdown?from=&to=&currency=&depth=` — spending per category (respecting hierarchy up to `depth` levels).
- `GET /pfm/reports/net-worth` — sum of all account balances (internal + external) converted to user's base currency.
- Currency conversion uses ECB daily rates (cached in Redis, refreshed by Celery task).
- All reports return `Content-Type: application/json` with standardised envelope `{ data, meta: { currency, period, generated_at } }`.
- Reports must respect GDPR: only return data for the authenticated user.
