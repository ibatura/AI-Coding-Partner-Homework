# Code Generation Agent

## Context

Read `specification.md` in the project root for the full system specification.
Read `sample-transactions.json` to understand input data shape (8 transactions including edge cases).

The pipeline uses **file-based JSON message passing** through `shared/` directories:
- `shared/input/` — messages awaiting processing
- `shared/processing/` — messages being actively processed (move here while working)
- `shared/output/` — messages ready for the next agent
- `shared/results/` — final results (both settled and rejected)

Standard message envelope format:
```json
{
  "message_id": "uuid4-string",
  "timestamp": "ISO-8601",
  "source_agent": "agent_name",
  "target_agent": "next_agent_name",
  "message_type": "transaction",
  "data": { ... original transaction fields plus agent-added fields ... }
}
```

## Task

Generate all pipeline code files in this order:

1. `agents/__init__.py` — empty Python package init
2. `agents/base_agent.py` — shared abstract base class with messaging utilities
3. `agents/transaction_validator.py` — validates fields, amounts, currencies
4. `agents/fraud_detector.py` — scores fraud risk 0–10
5. `agents/settlement_processor.py` — calculates fees, settles or holds
6. `integrator.py` — orchestrates the full pipeline

## Rules

- Use `decimal.Decimal` for ALL monetary math — NEVER use `float`
- Validate currencies against ISO 4217 whitelist: `{"USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"}`
- Mask account numbers in ALL log output (e.g., `ACC-1001` → `ACC-***1`)
- Each pipeline agent must extend `BaseAgent` and implement `process_message(self, message: dict) -> dict`
- Agents must NEVER crash on malformed input — write a rejection record instead
- All audit log entries must include: ISO 8601 timestamp, agent name, transaction_id, outcome
- File-based communication only — no in-memory queues, no direct function calls between agents
- Move message file to `shared/processing/` while processing; delete from there after writing result
- Rejected transactions go directly to `shared/results/` — they do NOT continue through the pipeline

## MCP

Use context7 to look up the Python `decimal` module documentation and the `logging` module patterns.
Document at least 2 queries in `research-notes.md` (one per library).

## Base Agent Design (`agents/base_agent.py`)

Create an abstract base class `BaseAgent` with:
- `__init__(self, name: str)` — sets agent name, calls `setup_logging()`
- `process_message(self, message: dict) -> dict` — abstract method (subclasses must implement)
- `read_message(self, filepath: str) -> dict` — reads and parses JSON from file
- `write_message(self, message: dict, directory: str) -> str` — writes JSON to directory, returns filepath
- `create_message_envelope(self, data: dict, target_agent: str, message_type: str) -> dict` — builds standard envelope with `uuid.uuid4()`, ISO timestamp, source_agent, target_agent
- `mask_pii(self, text: str) -> str` — masks account number patterns (e.g., `ACC-\d+` → `ACC-***<last digit>`)
- `setup_logging(self) -> logging.Logger` — configures structured audit logging to stdout

## Pipeline Agent Specifications

### Transaction Validator (`agents/transaction_validator.py`)
- Read message from `shared/input/`
- Validate required fields: `transaction_id`, `amount`, `currency`, `source_account`, `destination_account`, `timestamp`, `transaction_type`
- Parse `amount` with `decimal.Decimal` — reject if negative/zero with reason `"INVALID_AMOUNT"`
- Validate `currency` against ISO 4217 whitelist — reject if not found with reason `"INVALID_CURRENCY"`
- Validate `timestamp` is parseable ISO 8601 — reject if invalid with reason `"INVALID_TIMESTAMP"`
- Missing field → reject with reason `"MISSING_FIELD:<field_name>"`
- Validated: add `status="validated"`, `validated_at`, `validated_by="transaction_validator"`, set `target_agent="fraud_detector"`, write to `shared/output/`
- Rejected: add `status="rejected"`, `rejection_reason`, `rejected_at`, `rejected_by`, write to `shared/results/`
- Support `--dry-run` CLI flag: validate from `sample-transactions.json` without writing files, print summary table

### Fraud Detector (`agents/fraud_detector.py`)
- Read validated message from `shared/output/`
- Compute `fraud_risk_score` (integer 0–10):
  - +3 if `amount > 10000`
  - +4 if `amount > 50000` (cumulative with above, capped at 10)
  - +2 if transaction hour is 02:00–05:00 UTC
  - +1 if `metadata.country != "US"`
- Set `fraud_risk_level`: `"HIGH"` if score >= 7, `"MEDIUM"` if 4–6, `"LOW"` if 0–3
- Add `unusual_hour` (bool) and `cross_border` (bool) flags
- Add `fraud_checked_by="fraud_detector"`, `fraud_checked_at`
- Set `target_agent="settlement_processor"`, write to `shared/output/`

### Settlement Processor (`agents/settlement_processor.py`)
- Read fraud-scored message from `shared/output/`
- Calculate `fee_amount`: 0.1% of `amount` (min $0.50), plus $25.00 surcharge if `fraud_risk_level == "HIGH"`
- Set `settlement_status`:
  - `"HELD_FOR_REVIEW"` if `fraud_risk_level == "HIGH"`
  - `"SETTLED"` otherwise
- Add `fee_amount`, `net_amount` (amount - fee), `settlement_status`, `settled_by="settlement_processor"`, `settled_at`
- Write final result to `shared/results/<transaction_id>.json`

## Output

Create all files listed in the Task section above. The pipeline must be runnable via:
```bash
python integrator.py
```
