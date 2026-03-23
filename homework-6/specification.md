# Specification: AI-Powered Multi-Agent Banking Transaction Pipeline

## 1. High-Level Objective

Build a 3-agent Python pipeline that validates, scores for fraud risk, and settles banking transactions using file-based JSON message passing, with full audit logging, PII masking, and ISO 4217 currency enforcement.

---

## 2. Mid-Level Objectives

- Transactions with a currency code not in the ISO 4217 whitelist `['USD', 'EUR', 'GBP', 'JPY']` are rejected by the Transaction Validator with `status: "rejected"` and `reason: "INVALID_CURRENCY"` (covers TXN006 with currency "XYZ").
- Transactions with a non-positive amount (zero or negative) are rejected by the Transaction Validator with `status: "rejected"` and `reason: "INVALID_AMOUNT"` (covers TXN007 with amount "-100.00").
- Transactions above $10,000 USD-equivalent are flagged by the Fraud Detector with +3 score points (`fraud_risk_level: "MEDIUM"`); transactions above $50,000 receive +4 additional points (total +7, `fraud_risk_level: "HIGH"`). Covers TXN002 at $25,000 (score 3, MEDIUM) and TXN005 at $75,000 (score 7, HIGH).
- Transactions processed between 02:00 and 05:00 UTC receive a +2 fraud-risk-score penalty and are flagged with `unusual_hour: true` (covers TXN004 at 02:47 UTC).
- All 8 sample transactions are processed end-to-end; results for all 8 are written as individual JSON files to `shared/results/`, each containing final `status`, `fraud_risk_level`, `settlement_status`, and `fee_amount`.

---

## 3. Implementation Notes

- **Monetary calculations**: Use `decimal.Decimal` exclusively for all amounts, fees, and comparisons. Never use `float`. Initialise Decimal values from strings, not floats (e.g. `Decimal("1500.00")`).
- **Currency validation**: ISO 4217 whitelist enforced at validation stage: `['USD', 'EUR', 'GBP', 'JPY']`. Any other code → immediate rejection.
- **Audit logging**: Every agent operation writes a log entry containing:
  - `timestamp` — ISO 8601 format (e.g. `2026-03-16T09:00:00Z`)
  - `agent_name` — name of the agent writing the entry
  - `transaction_id` — the TXN identifier
  - `outcome` — one of: `validated`, `rejected`, `fraud_scored`, `settled`
- **PII masking**: Account numbers must never appear in plain text in logs. Mask to last-4 format: `ACC-1001` → `ACC-***1`. Apply masking before any log write.
- **File-based communication**: Agents communicate exclusively through JSON files in `shared/` subdirectories. No direct function calls or in-memory queues between agents.
- **Message format**: Every inter-agent JSON message must include:
  ```json
  {
    "message_id": "<UUID4>",
    "timestamp": "<ISO 8601>",
    "source_agent": "<agent_name>",
    "target_agent": "<next_agent_name>",
    "message_type": "transaction",
    "data": { ... }
  }
  ```
- **Error handling**: Agents must never crash on malformed or unexpected input. If a message cannot be processed, write a rejection record to `shared/results/` with the reason and continue to the next message.

---

## 4. Context

- **Beginning state**: `sample-transactions.json` exists in the project root with 8 raw transaction records. No agents exist. No `shared/` directories exist. No test files exist.

- **Ending state**:
  - `shared/input/`, `shared/processing/`, `shared/output/`, `shared/results/` directories created by the integrator on startup.
  - All 8 transactions from `sample-transactions.json` have been processed through the full pipeline.
  - 8 result JSON files are present in `shared/results/` (one per transaction).
  - An `audit.log` file records all agent operations with masked PII.
  - A test suite in `tests/` covers each agent with ≥ 90% code coverage.
  - `README.md` and `HOWTORUN.md` are complete and up to date.

---

## 5. Low-Level Tasks

### Task: Transaction Validator

**Prompt**:
```
Context: You are building agents/transaction_validator.py — a Python pipeline agent for a banking transaction system.
  It receives JSON messages from shared/input/ written by the integrator.
  The project uses decimal.Decimal for all monetary values (never float).
  Audit logs must mask account numbers (e.g. ACC-1001 → ACC-***1).
  Agents must not raise exceptions on bad input — write a rejection record instead.

Task: Implement process_message(message: dict) -> dict.
  The function must:
  1. Validate required fields are present: transaction_id, amount, currency, source_account, destination_account, timestamp.
  2. Convert amount to decimal.Decimal from string; reject if conversion fails.
  3. Reject if amount <= 0 with reason "INVALID_AMOUNT".
  4. Validate currency is in ISO 4217 whitelist ['USD', 'EUR', 'GBP', 'JPY']; reject with "INVALID_CURRENCY" if not.
  5. Return the full message dict with added fields: status ("validated" or "rejected"), and reason (if rejected).
  6. Write an audit log entry for every transaction processed.

Rules: Use decimal.Decimal only. Mask account numbers in all log output. Never raise; catch all exceptions.

Output: Return dict merging the input message data with status and optional reason fields.
```

**File to CREATE**: `agents/transaction_validator.py`

**Function to CREATE**: `process_message(message: dict) -> dict`

**Details**:
- Checks 6 required fields; rejects with `reason: "MISSING_FIELD:<field_name>"` if any are absent
- Rejects amounts that are zero, negative, or non-numeric (`reason: "INVALID_AMOUNT"`)
- Rejects currencies outside the whitelist (`reason: "INVALID_CURRENCY"`)
- Returns `status: "validated"` with original data for passing transactions
- Writes masked audit log entry regardless of outcome

---

### Task: Fraud Detector

**Prompt**:
```
Context: You are building agents/fraud_detector.py — a Python pipeline agent that receives validated
  transaction messages from shared/output/ (written by the Transaction Validator).
  Uses decimal.Decimal for all amount comparisons. Audit logging with PII masking required.
  Agents must not raise exceptions — write error records instead.

Task: Implement process_message(message: dict) -> dict.
  The function must score each validated transaction for fraud risk on a 0–10 scale:
  - Amount > $10,000 (USD-equivalent): +3 points
  - Amount > $50,000 (USD-equivalent): +4 additional points (total +7 for this tier)
  - Transaction hour (UTC) between 02:00 and 05:00: +2 points (unusual_hour flag = true)
  - Country in metadata is not "US": +1 point (cross-border flag = true)
  Map score to risk level: LOW (0–2), MEDIUM (3–6), HIGH (7–10).
  Return the message with added fields: fraud_risk_score (int), fraud_risk_level (str),
  unusual_hour (bool), cross_border (bool).

Rules: Use decimal.Decimal for all amount comparisons. Clamp score to 0–10. Log with masked PII.

Output: Return dict merging input data with fraud scoring fields.
```

**File to CREATE**: `agents/fraud_detector.py`

**Function to CREATE**: `process_message(message: dict) -> dict`

**Details**:
- Scores only validated transactions (status == "validated"); passes through rejected ones unchanged
- Uses `Decimal("10000")` and `Decimal("50000")` as threshold constants
- Parses UTC hour from `timestamp` field for unusual-hour detection
- Reads `metadata.country` for cross-border detection
- TXN002 ($25,000): score 3 → MEDIUM; TXN005 ($75,000): score 7 → HIGH; TXN004 (02:47, DE): score 3 → MEDIUM

---

### Task: Settlement Processor

**Prompt**:
```
Context: You are building agents/settlement_processor.py — the final Python pipeline agent.
  It receives fraud-scored messages and makes settlement decisions.
  Uses decimal.Decimal for all fee calculations. Audit logging with PII masking required.
  Agents must not raise exceptions — write error records to shared/results/ instead.

Task: Implement process_message(message: dict) -> dict.
  The function must:
  1. Skip (pass through as-is) any transaction with status == "rejected".
  2. For validated transactions, calculate a processing fee:
     - Standard fee: 0.1% of amount (Decimal("0.001") * amount), minimum Decimal("0.50")
     - HIGH fraud risk: add a flat Decimal("25.00") surcharge
  3. Determine settlement_status:
     - "settled" if fraud_risk_level is LOW
     - "settled_with_review" if fraud_risk_level is MEDIUM
     - "held_for_review" if fraud_risk_level is HIGH
     - "rejected" if original status was "rejected"
  4. Round fee to 2 decimal places using ROUND_HALF_UP.
  5. Write the final result JSON to shared/results/<transaction_id>.json.
  6. Return the complete message dict with fee_amount (str), settlement_status fields added.

Rules: Decimal only, ROUND_HALF_UP rounding, mask account numbers in logs.

Output: Return dict with all prior fields plus fee_amount and settlement_status.
```

**File to CREATE**: `agents/settlement_processor.py`

**Function to CREATE**: `process_message(message: dict) -> dict`

**Details**:
- Calculates fee as `max(amount * Decimal("0.001"), Decimal("0.50"))`, adding `Decimal("25.00")` surcharge for HIGH risk
- Writes final JSON result to `shared/results/<transaction_id>.json` after processing
- TXN001 ($1,500, LOW): fee $1.50, settled; TXN002 ($25,000, MEDIUM): fee $25.00, settled_with_review; TXN005 ($75,000, HIGH): held_for_review
- TXN006 and TXN007 reach this agent as rejected; settlement_status is set to "REJECTED", no fee calculated
