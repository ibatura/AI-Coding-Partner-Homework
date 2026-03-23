# Task 2.1 — Transaction Validator Agent (Python Code Output)

## Overview
The Transaction Validator is the **first agent in the pipeline**. It reads raw transactions from `shared/input/`, validates them against business rules, and writes validated messages to `shared/output/` or rejected messages to `shared/results/`.

**Note**: This file describes the **Python code** that the Code Generation sub-agent (`agents/code_generation_agent.md`) produces. The sub-agent MD file must contain instructions to generate this code.

## Step 1: Ensure the Sub-Agent MD File Exists
**Prerequisite**: `agents/code_generation_agent.md` must already exist (from Task 2, Step 1). The instructions in that MD file tell Claude to generate this Python code.

## Step 2: Create the Python Code File
**Output file**: `agents/transaction_validator.py`
- Must import from `agents/base_agent.py` (extends `BaseAgent`)
- Must implement `process_message(self, message: dict) -> dict`

---

## Step 3: Implement Validation Rules

### Required Field Checks
The validator must verify these fields exist and are non-empty:
- `transaction_id` (string)
- `amount` (string, parseable to Decimal)
- `currency` (string, 3 chars)
- `source_account` (string)
- `destination_account` (string)
- `timestamp` (string, valid ISO 8601)
- `transaction_type` (string)

If any required field is missing → reject with reason `"MISSING_FIELD:<field_name>"`

### Amount Validation
- Parse `amount` using `decimal.Decimal` (never `float`)
- Amount must be **positive** (> 0)
- If negative or zero → reject with reason `"INVALID_AMOUNT"`
- Note: TXN007 has amount `-100.00` and should be rejected here

### Currency Validation
- Validate against ISO 4217 whitelist: `{"USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"}`
- If currency not in whitelist → reject with reason `"INVALID_CURRENCY"`
- Note: TXN006 has currency `"XYZ"` and should be rejected here

### Timestamp Validation
- Must be parseable as ISO 8601 datetime
- Use `datetime.fromisoformat()` or similar
- If invalid → reject with reason `"INVALID_TIMESTAMP"`

---

## Step 4: Implement Output Behavior

### Validated transactions
- Add to data: `"status": "validated"`, `"validated_at": "<ISO-8601 timestamp>"`, `"validated_by": "transaction_validator"`
- Create message envelope with `target_agent: "fraud_detector"`
- Write JSON file to `shared/output/` with filename `{transaction_id}_validated.json`

### Rejected transactions
- Add to data: `"status": "rejected"`, `"rejection_reason": "<reason>"`, `"rejected_at": "<ISO-8601>"`, `"rejected_by": "transaction_validator"`
- Write JSON file to `shared/results/` with filename `{transaction_id}_rejected.json`
- Rejected transactions do NOT continue to the next agent

### Processing flow
- Move message file from `shared/input/` to `shared/processing/` while working
- After processing, write result to `shared/output/` or `shared/results/`
- Delete the file from `shared/processing/`

---

## Step 5: Implement Logging
- Log each validation decision with: timestamp, agent name, transaction_id, outcome (validated/rejected), reason if rejected
- Mask account numbers in log output (e.g., `ACC-1001` → `ACC-***1`)
- Use Python `logging` module with structured format

---

## Step 6: Add Dry-Run Mode
- Support `--dry-run` CLI flag (used by Task 3's `/validate-transactions` skill)
- In dry-run mode: validate all transactions from `sample-transactions.json` but do NOT write to `shared/` directories
- Instead, print a summary table: total, valid count, invalid count, reasons for each rejection

---

## Expected Behavior with Sample Data

| TXN ID | Amount     | Currency | Expected Result |
|--------|-----------|----------|-----------------|
| TXN001 | 1,500.00  | USD      | ✅ Validated     |
| TXN002 | 25,000.00 | USD      | ✅ Validated     |
| TXN003 | 9,999.99  | USD      | ✅ Validated     |
| TXN004 | 500.00    | EUR      | ✅ Validated     |
| TXN005 | 75,000.00 | USD      | ✅ Validated     |
| TXN006 | 200.00    | XYZ      | ❌ INVALID_CURRENCY |
| TXN007 | -100.00   | GBP      | ❌ INVALID_AMOUNT   |
| TXN008 | 3,200.00  | USD      | ✅ Validated     |

**Result**: 6 validated → `shared/output/`, 2 rejected → `shared/results/`

---

## Files Produced
- `agents/transaction_validator.py` (Python code, output of the sub-agent)

## Dependencies
- `agents/code_generation_agent.md` (the sub-agent that generates this code)
- `agents/base_agent.py` (must be generated first)
- `sample-transactions.json` (exists)

## Feeds Into
- Subtask 2.2 (Fraud Detector reads validated output)
