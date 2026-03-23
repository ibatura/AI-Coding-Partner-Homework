# Unit Test Agent

## Context

The banking pipeline is implemented in Python with these files:

- `agents/base_agent.py` — abstract base class with messaging utilities (read_message, write_message, create_message_envelope, mask_pii, setup_logging)
- `agents/transaction_validator.py` — validates fields, amounts, currencies; supports `--dry-run`
- `agents/fraud_detector.py` — scores fraud risk 0–10 based on amount, time, and geography
- `agents/settlement_processor.py` — applies fees, settles or holds based on risk level
- `integrator.py` — orchestrates the full pipeline (setup_directories, load_transactions, write_input_envelopes, run_pipeline)

Read each source file before writing tests. Use `sample-transactions.json` to understand the 8 real test cases including the 2 edge-case rejections (TXN006: bad currency, TXN007: negative amount).

## Task

Generate a comprehensive test suite in `tests/` with ≥ 90% code coverage:

1. `tests/__init__.py` — empty package init
2. `tests/conftest.py` — shared pytest fixtures using `tmp_path`
3. `tests/test_base_agent.py` — tests for BaseAgent utilities
4. `tests/test_transaction_validator.py` — unit tests for all validation rules
5. `tests/test_fraud_detector.py` — unit tests for all scoring paths and risk levels
6. `tests/test_settlement_processor.py` — unit tests for fees, settlement, and hold logic
7. `tests/test_integration.py` — end-to-end pipeline test using real sample data

## Rules

- Use `pytest` and `pytest-cov`
- **All file I/O must use `tmp_path`** — never write to the real `shared/` directories
- Cover every validation rule branch (missing field, invalid amount, invalid currency, invalid timestamp)
- Cover every fraud scoring path (+3, +4, +2, +1 rules and cap at 10)
- Cover every settlement branch (LOW → settled, MEDIUM → settled_with_review, HIGH → held_for_review)
- Test fee calculation: min fee ($0.50), normal fee, max fee ($50.00)
- Include the 2 rejection edge cases from sample data (TXN006, TXN007)
- Integration test must run the full pipeline and verify all 8 transactions land in shared/results/
- Target ≥ 90% code coverage; minimum gate is 80%

## Output

Create all test files listed above. Tests must pass via:
```bash
pytest -v --cov=agents --cov=integrator --cov-report=term-missing
```
