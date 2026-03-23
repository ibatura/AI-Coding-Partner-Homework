# Task 5.1 — Unit & Integration Tests (Output of Agent 3 Sub-Agent)

## Overview
Write a comprehensive test suite covering each pipeline agent and the full integration pipeline. Coverage must be ≥ 80% (hook gate) with a target of ≥ 90%.

**Note**: These test files are the **output** of the Unit Test sub-agent (`agents/unit_test_agent.md`). The sub-agent MD file contains the instructions for Claude to generate this code.

---

## Step 1: Ensure the Sub-Agent MD File Exists
**Prerequisite**: `agents/unit_test_agent.md` must already exist (from Task 3, Step 1). That MD file tells Claude what tests to generate.

## Step 2: Set Up Test Infrastructure

### Install dependencies
```bash
pip install pytest pytest-cov
```

### Create test directory structure (output of the sub-agent)
```
tests/
├── __init__.py
├── conftest.py                    ← shared fixtures
├── test_transaction_validator.py
├── test_fraud_detector.py
├── test_settlement_processor.py
├── test_base_agent.py
└── test_integration.py
```

### Create `conftest.py` — Shared Fixtures

Must include:
- **`tmp_shared_dirs` fixture**: Creates temporary `shared/input/`, `shared/processing/`, `shared/output/`, `shared/results/` directories using `tmp_path`. This isolates tests from the real `shared/` directory.
- **`sample_transaction` fixture**: Returns a valid sample transaction dict (e.g., TXN001 data)
- **`sample_transactions` fixture**: Returns the full list of 8 transactions from `sample-transactions.json`
- **`valid_message_envelope` fixture**: Returns a properly formatted message envelope wrapping a sample transaction
- **`invalid_transaction_negative_amount` fixture**: TXN007 data
- **`invalid_transaction_bad_currency` fixture**: TXN006 data
- **`high_value_transaction` fixture**: TXN005 data ($75,000)
- **`unusual_hour_transaction` fixture**: TXN004 data (02:47 AM)

---

## Step 3: Transaction Validator Tests (`test_transaction_validator.py`)

### Unit tests to write:

1. **`test_valid_transaction_passes`**: Normal transaction (TXN001) → status "validated"
2. **`test_negative_amount_rejected`**: TXN007 → rejected with "INVALID_AMOUNT"
3. **`test_zero_amount_rejected`**: Amount "0.00" → rejected with "INVALID_AMOUNT"
4. **`test_invalid_currency_rejected`**: TXN006 ("XYZ") → rejected with "INVALID_CURRENCY"
5. **`test_missing_field_rejected`**: Transaction missing `transaction_id` → rejected with "MISSING_FIELD:transaction_id"
6. **`test_missing_amount_rejected`**: Transaction missing `amount` → rejected
7. **`test_valid_currencies_accepted`**: Test each: USD, EUR, GBP, JPY → all pass
8. **`test_amount_uses_decimal`**: Verify amount is processed as `Decimal`, not `float`
9. **`test_output_contains_required_fields`**: Validated output has `status`, `validated_at`, `validated_by`
10. **`test_rejected_output_contains_reason`**: Rejected output has `status`, `rejection_reason`
11. **`test_dry_run_mode`**: Dry-run does not write files to `shared/`

---

## Step 4: Fraud Detector Tests (`test_fraud_detector.py`)

### Unit tests to write:

1. **`test_low_risk_normal_transaction`**: $1,500 daytime US → score 0, level LOW
2. **`test_high_value_medium_risk`**: $25,000 → score 3, level MEDIUM (HIGH_VALUE flag)
3. **`test_very_high_value_high_risk`**: $75,000 → score 7, level HIGH (HIGH_VALUE + VERY_HIGH_VALUE)
4. **`test_unusual_hour_scoring`**: 02:47 AM → +2 points (UNUSUAL_HOUR flag)
5. **`test_cross_border_scoring`**: Country "DE" → +1 point (CROSS_BORDER flag)
6. **`test_combined_flags`**: $500 at 02:47 from DE → score 3 (UNUSUAL_HOUR + CROSS_BORDER)
7. **`test_just_under_threshold`**: $9,999.99 → score 0, level LOW (no HIGH_VALUE flag)
8. **`test_exactly_at_threshold`**: $10,000.00 → should NOT trigger (> not >=), score 0 — OR if implemented as >=, then score 3. Document the decision.
9. **`test_output_contains_fraud_fields`**: Output has `fraud_risk_score`, `fraud_risk_level`, `fraud_flags`
10. **`test_all_risk_levels_reachable`**: At least one test for each level (LOW, MEDIUM, HIGH)

---

## Step 5: Settlement Processor Tests (`test_settlement_processor.py`)

### Unit tests to write:

1. **`test_low_risk_settled`**: LOW risk → status "settled", fee calculated
2. **`test_medium_risk_settled_with_review`**: MEDIUM risk → status "settled_with_review"
3. **`test_high_risk_held`**: HIGH risk → status "held_for_review", fee $0.00
4. **`test_fee_calculation_standard`**: $1,500 → fee = $1.50 (0.1%)
5. **`test_fee_minimum`**: $100 → fee = $0.50 (minimum floor)
6. **`test_fee_maximum`**: $75,000 → fee = $50.00 (maximum cap)
7. **`test_fee_uses_decimal`**: Verify fee calculation uses `Decimal`, not `float`
8. **`test_net_amount_calculation`**: amount - fee = net_amount
9. **`test_settlement_id_generated`**: Output includes `settlement_id` starting with "STL-"
10. **`test_held_transaction_no_settlement_id`**: Held transactions have null settlement_id
11. **`test_pipeline_summary_generated`**: After processing all, `pipeline_summary.json` is created

---

## Step 6: Base Agent Tests (`test_base_agent.py`)

### Unit tests to write:

1. **`test_create_message_envelope`**: Verify envelope has all required fields (message_id, timestamp, source_agent, etc.)
2. **`test_message_id_is_uuid`**: Verify message_id is valid UUID4
3. **`test_timestamp_is_iso8601`**: Verify timestamp format
4. **`test_mask_pii_account_number`**: "ACC-1001" → "ACC-***1"
5. **`test_read_write_message`**: Write JSON to temp dir, read it back, verify match
6. **`test_write_message_creates_file`**: File exists after write

---

## Step 7: Integration Test (`test_integration.py`)

### End-to-end tests:

1. **`test_full_pipeline_runs`**: Load all 8 transactions, run full pipeline, verify 8 results in `shared/results/`
2. **`test_rejected_transactions_in_results`**: TXN006 and TXN007 are in results with rejected status
3. **`test_settled_transactions_in_results`**: TXN001, TXN003, TXN008 are settled
4. **`test_high_risk_held_in_results`**: TXN005 is held for review
5. **`test_pipeline_summary_exists`**: `pipeline_summary.json` exists after run
6. **`test_pipeline_summary_counts`**: Summary has correct counts (settled=3, review=2, held=1, rejected=2)
7. **`test_no_files_in_processing`**: After pipeline completes, `shared/processing/` is empty
8. **`test_result_files_are_valid_json`**: All files in `shared/results/` are parseable JSON

### Important: Isolation
- All integration tests must use `tmp_path` for `shared/` directories
- Never read/write to the real `shared/` directory during tests
- Set up and tear down temp directories in fixtures

---

## Step 8: Run and Verify Coverage

```bash
# Run with coverage report
pytest --cov=agents --cov=integrator --cov-report=term-missing --cov-report=html -v

# Verify gate threshold
pytest --cov=agents --cov=integrator --cov-fail-under=80
```

### Coverage targets:
- **Gate (minimum)**: 80% — hook blocks push below this
- **Target**: 90%+ — aim for this
- **Focus areas**: All `process_message()` methods, all validation branches, all risk scoring paths

---

## Files Produced (by the Unit Test sub-agent)
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_transaction_validator.py`
- `tests/test_fraud_detector.py`
- `tests/test_settlement_processor.py`
- `tests/test_base_agent.py`
- `tests/test_integration.py`

## Dependencies
- `agents/unit_test_agent.md` (the sub-agent MD file that generates these tests)
- All pipeline Python code from Task 2
- `pytest` and `pytest-cov` installed
- `integrator.py` for integration tests

## Feeds Into
- Task 3.2 (coverage gate hook uses these tests)
- Screenshot: `docs/screenshots/test-coverage.png`
