# [Smart Spend Analyzer & Budgeter] Specification

## High-Level Objective
- Develop a comprehensive Personal Financial Management (PFM) module that aggregates transaction data across internal bank cards and external manual sources (cash, other bank accounts). The system must support hierarchical categorization, custom category creation, machine-learning-ready category overrides, and scheduled spending projections.

## Mid-Level Objectives
- **Compliance:** Ensure all data aggregation and manual entries comply with PSD2 and financial reporting standards of the Bank.
- **Security:** Encrypt manual "External Source" data at rest; ensure users can only see their own financial data (Multi-tenancy isolation).
- **Audit:** Log all manual category overrides and custom data injections for fraud detection and system auditing.
- **Performance:** Optimize recursive queries for tree-structured category reporting to ensure sub-second UI responses.
- **Integration:** Hook into the existing Transaction Processing Engine to intercept transaction codes for real-time auto-categorization.

## Implementation Notes
- **Data Privacy:** Strictly adhere to GDPR; manual entries must be deletable by the user ("Right to be forgotten").
- **Audit Trail:** Maintain a history of category changes to train future auto-categorization models.
- **Validation:** Sanitize all custom category names and manual entry descriptions to prevent XSS/Injection.
- **Precision:** Use **Decimal** for all monetary calculations to avoid floating-point errors.
- **Testing:** Unit tests for tree-traversal logic and integration tests for transaction code mapping.

## Context

### Beginning context
- Core Banking System (CBS) with existing `Transactions`, `Cards`, and `Accounts` tables.
- Standard ISO-8583 or proprietary transaction codes (MCC - Merchant Category Codes).
- Existing User Authentication and Session Management.

### Ending context
- New `SpendReports` dashboard.
- New Data Models: `TransactionCategory` (Self-referencing), `ManualTransactionSource`, and `CategoryOverride`.
- API endpoints for CRUD operations on custom categories and templates.
- Scheduled task engine for "Projected Spend" templates.

---

## Low-Level Tasks

### 1. [Database & Schema Task]
**What prompt would you run to complete this task?**
"Create a migration script for the PFM module. Include a self-referencing `Categories` table for tree structures, a `ManualSources` table for external cards/cash, and a `CategoryMapping` table to store user-defined overrides for specific transaction codes."

**What file do you want to CREATE or UPDATE?**
`/database/migrations/2026_02_09_create_pfm_schema.sql`

**What function do you want to CREATE or UPDATE?**
`up()` and `down()` migration methods.

**What are details you want to add to drive the code changes?**
- `Categories` table needs: `id`, `parent_id` (nullable), `name`, `user_id` (nullable for system defaults).
- `ManualSources` types: `CASH`, `EXTERNAL_CARD`, `EXTERNAL_LOAN`, `CRYPTO`.
- Add `is_custom` boolean to differentiate between system and user categories.

### 2. [Business Logic: Tree Reporting]
**What prompt would you run to complete this task?**
"Implement a service that calculates total spend per category. It must support deep reporting, meaning a parent category's total includes the sum of all its sub-categories recursively."

**What file do you want to CREATE or UPDATE?**
`/services/ReportingService.js`

**What function do you want to CREATE or UPDATE?**
`getDeepSpendReport(userId, startDate, endDate)`

**What are details you want to add to drive the code changes?**
- Use a recursive Common Table Expression (CTE) or a recursive code-level function to aggregate totals.
- Ensure the result returns a JSON tree structure suitable for a "Drill-down" UI.

### 3. [Logic Task: Auto-Categorization & Overrides]
**What prompt would you run to complete this task?**
"Create a function that assigns a category to a transaction. Check first for a user-specific override in `CategoryMapping`, then fallback to the default system mapping based on the transaction code."

**What file do you want to CREATE or UPDATE?**
`/services/CategorizationEngine.js`

**What function do you want to CREATE or UPDATE?**
`assignCategory(transactionId, transactionCode, userId)`

**What are details you want to add to drive the code changes?**
- If a user manually changes a category, save the `transaction_code` + `category_id` pair to `CategoryMapping` so future transactions with that code are auto-categorized correctly for that specific user.

### 4. [Templates & Scheduled Spend]
**What prompt would you run to complete this task?**
"Implement a Spend Template system where users can define recurring manual costs (e.g., 'Monthly Cash Rent'). Create a logic to project these into the 'Spend Report' for future dates."

**What file do you want to CREATE or UPDATE?**
`/models/SpendTemplate.js` and `/services/ProjectionService.js`

**What function do you want to CREATE or UPDATE?**
`generateProjectedSpend(userId, month)`

**What are details you want to add to drive the code changes?**
- Template types: `Fixed` (same amount), `Variable` (estimated amount).
- Frequencies: `Weekly`, `Monthly`, `Quarterly`.
- Use **Decimal** for the `estimated_amount`.