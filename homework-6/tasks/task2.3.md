# Task 2.3 — Settlement Processor Agent (Python Code Output)

## Overview
The Settlement Processor is the **third and final agent in the pipeline**. It reads fraud-scored transactions from `shared/output/`, applies settlement logic (fees, holds, approvals), and writes final results to `shared/results/`.

**Note**: This file describes the **Python code** that the Code Generation sub-agent (`agents/code_generation_agent.md`) produces. The sub-agent MD file must contain instructions to generate this code.

## Step 1: Ensure the Sub-Agent MD File Exists
**Prerequisite**: `agents/code_generation_agent.md` must already exist (from Task 2, Step 1).

## Step 2: Create the Python Code File
**Output file**: `agents/settlement_processor.py`
- Must import from `agents/base_agent.py` (extends `BaseAgent`)
- Must implement `process_message(self, message: dict) -> dict`

---

## Step 3: Implement Settlement Logic

### Settlement Rules

1. **HIGH risk transactions** (`fraud_risk_level == "HIGH"`):
   - Status: `"held_for_review"`
   - Do NOT settle — flag for manual review
   - Add `"hold_reason": "HIGH_FRAUD_RISK"`
   - No fee calculated

2. **MEDIUM risk transactions** (`fraud_risk_level == "MEDIUM"`):
   - Status: `"settled_with_review"`
   - Settle but flag for review
   - Apply standard fee

3. **LOW risk transactions** (`fraud_risk_level == "LOW"`):
   - Status: `"settled"`
   - Settle normally
   - Apply standard fee

### Fee Calculation
- Use `decimal.Decimal` for all calculations
- Base fee: 0.1% of transaction amount (0.001)
- Minimum fee: $0.50
- Maximum fee: $50.00
- Fee formula: `max(min(amount * Decimal("0.001"), Decimal("50.00")), Decimal("0.50"))`
- For held transactions: fee = $0.00 (not settled)
- Rounding: ROUND_HALF_UP to 2 decimal places

### Settlement ID Generation
- Generate a unique settlement ID: `"STL-{uuid4-short}"` (first 8 chars of uuid4)

---

## Step 4: Implement Output Behavior

### Final result format
Add to data:
- `"settlement_status": "settled" | "settled_with_review" | "held_for_review"`
- `"settlement_id": "STL-xxxxxxxx"` (or null if held)
- `"settlement_fee": "0.50"` (Decimal as string)
- `"net_amount": "1499.50"` (amount minus fee, Decimal as string)
- `"settled_at": "<ISO-8601>"` (or null if held)
- `"settled_by": "settlement_processor"`
- `"pipeline_complete": true`

### Write to `shared/results/`
- Filename: `{transaction_id}_result.json`
- This is the **final destination** for all transactions
- Include the full message envelope with complete processing history

### Processing flow
- Read `*_scored.json` files from `shared/output/`
- Move to `shared/processing/` while working
- Write `*_result.json` to `shared/results/`
- Clean up `shared/processing/`

---

## Step 5: Implement Logging
- Log each settlement decision: timestamp, agent name, transaction_id, settlement_status, fee, net_amount
- Mask account numbers in all log output
- Held transactions should log at WARNING level

---

## Step 6: Generate Pipeline Summary

After processing all transactions, create a summary file `shared/results/pipeline_summary.json`:
```json
{
  "run_id": "uuid4",
  "completed_at": "ISO-8601",
  "total_transactions": 8,
  "settled": 3,
  "settled_with_review": 2,
  "held_for_review": 1,
  "rejected": 2,
  "total_fees_collected": "5.50",
  "total_volume_processed": "105199.99",
  "transactions": [ ... summary of each ]
}
```

---

## Expected Behavior with Sample Data

| TXN ID | Amount     | Risk Level | Settlement Status    | Fee    | Net Amount  |
|--------|-----------|------------|---------------------|--------|-------------|
| TXN001 | 1,500.00  | LOW        | settled             | $1.50  | $1,498.50   |
| TXN002 | 25,000.00 | MEDIUM     | settled_with_review | $25.00 | $24,975.00  |
| TXN003 | 9,999.99  | LOW        | settled             | $10.00 | $9,989.99   |
| TXN004 | 500.00    | MEDIUM     | settled_with_review | $0.50  | $499.50     |
| TXN005 | 75,000.00 | HIGH       | held_for_review     | $0.00  | $75,000.00  |
| TXN008 | 3,200.00  | LOW        | settled             | $3.20  | $3,196.80   |

Plus 2 rejected transactions (TXN006, TXN007) already in `shared/results/` from validator.

**Final count in `shared/results/`**: 8 files (6 settled/held + 2 rejected) + 1 summary = 9 files total.

---

## Files Produced
- `agents/settlement_processor.py` (Python code, output of the sub-agent)

## Dependencies
- `agents/code_generation_agent.md` (the sub-agent that generates this code)
- `agents/base_agent.py` (must exist)
- Subtask 2.2 output (scored transactions in `shared/output/`)

## Feeds Into
- Task 4 (MCP server reads from `shared/results/`)
- Task 5 (tests verify settlement logic)
