# Homework 3: Specification-Driven Design

## Student & Task Summary

**Student**: Ivan Batura

**Task**: Design a specification package for a **Personal Financial Management (PFM)** module within an existing internal banking system. The module provides account aggregation across internal and external sources, hierarchical transaction categorisation, scheduled spending projections, and compliance-ready financial reporting — all governed by PSD2, GDPR, and PCI DSS requirements.

**Deliverables produced**:
| File | Purpose |
|------|---------|
| `specification.md` | Full product spec: high-level objective, 6 mid-level objectives, implementation notes, beginning/ending context, and 17 low-level implementation tasks |
| `agents.md` | AI agent configuration: tech stack rules, domain conventions, code style, security constraints, testing expectations, and behavioural guidelines |
| `.claude/CLAUDE.md` | Claude Code editor rules: mandatory patterns, naming conventions, things to avoid, and compliance-first decision framework |

---

## Rationale

### Why This Specification Structure

The specification follows a **three-tier decomposition** (high → mid → low) because AI coding agents perform best when given:

1. **A single high-level objective** that anchors every decision. Without it, agents drift between features and optimise locally instead of globally. The PFM spec's one-sentence objective ("unified view of finances ... while meeting PSD2, GDPR, and PCI DSS") gives the agent a north star for every trade-off.

2. **Mid-level objectives that are testable**. Each of the six objectives (account foundation, aggregation, categorisation, projections, compliance, overrides) maps to a distinct capability that can be verified independently. This lets the agent work on one feature at a time without losing coherence, and lets reviewers check completeness at a glance.

3. **Low-level tasks with explicit file paths, function names, and implementation details**. Vague prompts produce vague code. Each of the 17 tasks tells the agent exactly what to create, where to put it, and what constraints to follow. This eliminates ambiguity around "should I create a new file or modify an existing one?" and ensures the agent's output is deterministic and reviewable.

### Why Separate `agents.md` from `CLAUDE.md`

- `agents.md` is **tool-agnostic**: it defines domain rules, tech stack, and coding conventions that apply whether you use Claude Code, Copilot, Cursor, or a future tool. It reads like a team onboarding guide for an AI colleague.
- `.claude/CLAUDE.md` is **tool-specific**: it uses the format and conventions that Claude Code loads automatically, with short imperative rules optimised for the model's instruction-following. This separation means switching AI tools requires only swapping the editor rules file, not rewriting domain knowledge.

### Why 17 Low-Level Tasks (Not Fewer or More)

The task count follows the natural module boundaries: 3 schema tasks (accounts, transactions, categories), 2 aggregation tasks (Open Banking adapter, manual entry), 2 categorisation tasks (auto-categoriser, CRUD/tree), 2 projection tasks (engine, reminders), 3 compliance tasks (GDPR, PCI, audit), 1 i18n task, 1 API wiring task, 2 testing tasks (unit, integration), and 1 reporting task. Each task is scoped to be completable in a single AI session (~30–60 minutes of agent work) — small enough to review meaningfully, large enough to produce a working component.

---

## Industry Best Practices

Below are the FinTech/banking best practices incorporated into the specification and where they appear.

### 1. Decimal Arithmetic for Money (IEEE 754 Avoidance)

**Where it appears**: `specification.md` — Implementation Notes > Technical Constraints; `agents.md` — Section 3 (Monetary Values); `.claude/CLAUDE.md` — Rule 1.

**Practice**: Financial systems must never use binary floating-point for monetary values because IEEE 754 floats cannot exactly represent most decimal fractions (e.g., `0.1 + 0.2 ≠ 0.3`). The industry standard is fixed-point decimal or integer-minor-unit representation. This spec mandates Python's `decimal.Decimal` and PostgreSQL's `Numeric(19,4)` with banker's rounding (`ROUND_HALF_EVEN`), consistent with the practices recommended by Martin Fowler's Money pattern and used in production at Stripe, Wise, and major banks.

### 2. PSD2 Consent Lifecycle (Strong Customer Authentication)

**Where it appears**: `specification.md` — Mid-Level Objective 2 (Account Aggregation), Low-Level Task 4 (Open Banking Adapter); `agents.md` — Section 6 (PSD2 constraints).

**Practice**: The EU's PSD2 directive requires that account information service providers (AISPs) obtain explicit user consent before accessing account data, with consent that has a defined scope, expiry (max 90 days per regulatory guidance), and is revocable at any time. The spec models the full consent lifecycle: creation with SCA, token storage, automatic expiry checking via scheduled tasks, and user-initiated revocation — matching the Berlin Group NextGenPSD2 implementation guidelines used across European banking.

### 3. GDPR Right-to-Erasure with Audit Trail Preservation

**Where it appears**: `specification.md` — Mid-Level Objective 5, Low-Level Task 10 (GDPR Erasure & Export); `agents.md` — Section 6 (GDPR constraints).

**Practice**: GDPR Article 17 grants users the right to erasure, but financial regulations (e.g., Anti-Money Laundering directives) require retention of audit records for 5–7+ years. The spec resolves this tension by performing hard deletion of all personal data while anonymising (not deleting) audit log entries — replacing the `user_id` with a one-way hash and retaining only the action and timestamp. This approach follows the ICO (UK) and CNIL (France) guidance on balancing erasure with legitimate retention obligations.

### 4. PCI DSS Tokenisation and Field-Level Encryption

**Where it appears**: `specification.md` — Implementation Notes > Security, Low-Level Tasks 11 (PCI & Encryption); `agents.md` — Section 5 (Data Protection); `.claude/CLAUDE.md` — Rules 4 and 5.

**Practice**: PCI DSS requires that cardholder data (PANs) never be stored in plaintext and that access is restricted on a need-to-know basis. The spec implements: (a) tokenisation so full PANs are never stored in PFM tables, (b) AES-256-GCM field-level encryption for sensitive user content (notes, tags), (c) KEK/DEK key hierarchy with rotation support, and (d) log scanning to mask PAN patterns before they hit storage. This mirrors the approach used by payment processors like Adyen and Stripe.

### 5. Immutable Append-Only Audit Log

**Where it appears**: `specification.md` — Implementation Notes > Audit & Logging, Low-Level Task 12; `agents.md` — Section 3 (Account & Transaction Integrity).

**Practice**: Regulatory environments require tamper-evident audit trails. The spec enforces append-only semantics by restricting the application database role to INSERT-only on the audit table (no UPDATE/DELETE), storing structured JSON events with correlation IDs, and configuring retention periods of 7+ years with archival to cold storage. This aligns with SOX (Sarbanes-Oxley) audit trail requirements and EBA (European Banking Authority) guidelines on record-keeping.

### 6. Hierarchical Categorisation with ltree

**Where it appears**: `specification.md` — Mid-Level Objective 3, Low-Level Tasks 3 and 7; `agents.md` — Section 2 (Database rules).

**Practice**: Financial categorisation systems commonly require arbitrary nesting (e.g., Transport > Public > Rail). PostgreSQL's `ltree` extension provides O(1) ancestor/descendant queries via materialised path indexing, avoiding the performance degradation of recursive CTEs on deep trees. This is the same approach used by accounting platforms (e.g., Xero, QuickBooks) for chart-of-accounts hierarchies and by Plaid for their transaction category taxonomy.

### 7. RFC 7807 Problem Details for Error Responses

**Where it appears**: `specification.md` — Implementation Notes > Error Handling; `.claude/CLAUDE.md` — Error Pattern section.

**Practice**: RFC 7807 (Problem Details for HTTP APIs) provides a standardised JSON error format (`type`, `title`, `status`, `detail`, `instance`) that makes errors machine-parseable and consistent across endpoints. This is increasingly adopted in financial APIs — the Berlin Group NextGenPSD2 spec mandates it, and the UK Open Banking standard uses a similar structured error format.

### 8. Category Overrides as ML Training Data

**Where it appears**: `specification.md` — Mid-Level Objective 6, Low-Level Tasks 3 and 6; `agents.md` — Section 3 (Categorisation rules).

**Practice**: Storing user categorisation overrides alongside the original system-assigned category creates labelled training pairs `(transaction_features, correct_category)` that can improve auto-categorisation models over time. This human-in-the-loop pattern is used by personal finance apps like Mint, YNAB, and Emma to continuously improve categorisation accuracy as users correct the system's predictions.

### 9. Correlation ID Propagation

**Where it appears**: `specification.md` — Implementation Notes > Audit & Logging, Low-Level Task 14 (middleware); `agents.md` — Section 8 (Debugging guidelines).

**Practice**: Distributed tracing via correlation IDs (passed in `X-Correlation-ID` headers) is essential for debugging in microservice and modular monolith architectures. Every log line, audit event, and outgoing HTTP call includes the same correlation ID, enabling end-to-end request tracing. This follows the OpenTelemetry and W3C Trace Context standards adopted across the financial services industry.

### 10. Multi-Currency with ISO 4217 and ECB Rates

**Where it appears**: `specification.md` — Mid-Level Objective 1, Low-Level Tasks 1 and 2; `agents.md` — Section 3 (Multi-Currency).

**Practice**: Storing both the original amount/currency and the converted amount on every transaction ensures no information is lost and conversions are auditable. Using ECB daily reference rates (freely available, widely trusted in EU banking) with Redis caching follows the approach used by multi-currency banking platforms like Revolut and N26 for non-trading-grade FX.
