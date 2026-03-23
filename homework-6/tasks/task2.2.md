# Task 2.2 — Fraud Detector Agent (Python Code Output)

## Overview
The Fraud Detector is the **second agent in the pipeline**. It reads validated transactions from `shared/output/`, calculates a fraud risk score (0–10 scale), assigns a risk level, and passes them to the next agent.

**Note**: This file describes the **Python code** that the Code Generation sub-agent (`agents/code_generation_agent.md`) produces. The sub-agent MD file must contain instructions to generate this code.

## Step 1: Ensure the Sub-Agent MD File Exists
**Prerequisite**: `agents/code_generation_agent.md` must already exist (from Task 2, Step 1).

## Step 2: Create the Python Code File
**Output file**: `agents/fraud_detector.py`
- Must import from `agents/base_agent.py` (extends `BaseAgent`)
- Must implement `process_message(self, message: dict) -> dict`

---

## Step 3: Implement Risk Scoring System

### Scoring Rules (additive points, 0–10 scale)

| Rule | Condition | Points |
|------|-----------|--------|
| High value | `amount > 10,000` | +3 |
| Very high value | `amount > 50,000` | +4 (additional, so total +7 for >50K) |
| Unusual hour | Transaction timestamp hour between 02:00–04:59 (inclusive) | +2 |
| Cross-border | `metadata.country` is not "US" (or differs from source account country) | +1 |

**Important**: Points are additive. A $75,000 transaction at 3am from Germany would score: +3 (>10K) + 4 (>50K) + 2 (unusual hour) + 1 (cross-border) = 10.

### Risk Level Assignment

| Score Range | Risk Level |
|------------|------------|
| 0–2        | LOW        |
| 3–6        | MEDIUM     |
| 7–10       | HIGH       |

---

## Step 4: Implement Output Behavior

### All transactions (validated ones only reach this agent)
- Add to data:
  - `"fraud_risk_score": <int>`
  - `"fraud_risk_level": "LOW" | "MEDIUM" | "HIGH"`
  - `"fraud_flags": [<list of triggered rules>]` (e.g., `["HIGH_VALUE", "UNUSUAL_HOUR"]`)
  - `"fraud_checked_at": "<ISO-8601>"`
  - `"fraud_checked_by": "fraud_detector"`
- Create message envelope with `target_agent: "settlement_processor"`
- Write JSON file to `shared/output/` with filename `{transaction_id}_scored.json`
- Remove the `_validated.json` input file from `shared/output/` after processing

### Processing flow
- Read `*_validated.json` files from `shared/output/`
- Move to `shared/processing/` while working
- Write `*_scored.json` to `shared/output/`
- Clean up `shared/processing/`

---

## Step 5: Implement Logging
- Log each scoring decision: timestamp, agent name, transaction_id, score, risk level, triggered flags
- Mask account numbers in all log output
- HIGH risk transactions should log at WARNING level

---

## Expected Behavior with Sample Data

Only the 6 validated transactions reach this agent:

| TXN ID | Amount     | Hour  | Country | Score | Level  | Flags |
|--------|-----------|-------|---------|-------|--------|-------|
| TXN001 | 1,500.00  | 09:00 | US      | 0     | LOW    | (none) |
| TXN002 | 25,000.00 | 09:15 | US      | 3     | MEDIUM | HIGH_VALUE |
| TXN003 | 9,999.99  | 09:30 | US      | 0     | LOW    | (none) |
| TXN004 | 500.00    | 02:47 | DE      | 3     | MEDIUM | UNUSUAL_HOUR, CROSS_BORDER |
| TXN005 | 75,000.00 | 10:00 | US      | 7     | HIGH   | HIGH_VALUE, VERY_HIGH_VALUE |
| TXN008 | 3,200.00  | 10:15 | US      | 0     | LOW    | (none) |

---

## Files Produced
- `agents/fraud_detector.py` (Python code, output of the sub-agent)

## Dependencies
- `agents/code_generation_agent.md` (the sub-agent that generates this code)
- `agents/base_agent.py` (must exist)
- Subtask 2.1 output (validated transactions in `shared/output/`)

## Feeds Into
- Subtask 2.3 (Settlement Processor reads scored output)
