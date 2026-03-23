# How to Run — AI-Powered Multi-Agent Banking Transaction Pipeline

Step-by-step guide to set up, run, and test the pipeline.

---

## Prerequisites

- **Python 3.9 or higher**
  ```bash
  python3 --version   # must print Python 3.9.x or higher
  ```
- **pip** (bundled with Python 3.4+)
  ```bash
  pip --version
  ```
- **Git** (to clone the repository)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/IvanBatura/AI-Coding-Partner-Homework.git
cd AI-Coding-Partner-Homework/homework-6
```

If you already have the repo, just navigate to the `homework-6` directory:

```bash
cd /path/to/AI-Coding-Partner-Homework/homework-6
```

---

## Step 2: Install Dependencies

```bash
pip install fastmcp pytest pytest-cov
```

Or, if a `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastmcp-x.x.x pytest-x.x.x pytest-cov-x.x.x ...
```

---

## Step 3: Verify Sample Transactions Exist

The pipeline reads from `sample-transactions.json` in the project root:

```bash
python3 -c "import json; txns = json.load(open('sample-transactions.json')); print(f'Found {len(txns)} transactions')"
```

**Expected output:**
```
Found 8 transactions
```

---

## Step 4: Run the Full Pipeline

```bash
python3 integrator.py
```

The integrator will:
1. Create `shared/input/`, `shared/processing/`, `shared/output/`, `shared/results/` if they don't exist
2. Load all 8 transactions from `sample-transactions.json`
3. Run Transaction Validator → Fraud Detector → Settlement Processor sequentially
4. Write results to `shared/results/`

**Expected output (abbreviated):**
```
2026-03-23T10:00:00 | integrator | INFO | Pipeline starting — 8 transactions
2026-03-23T10:00:00 | integrator | INFO | Transaction Validator processing...
2026-03-23T10:00:00 | integrator | INFO | Fraud Detector processing...
2026-03-23T10:00:00 | integrator | INFO | Settlement Processor processing...
2026-03-23T10:00:00 | integrator | INFO | Pipeline complete
```

---

## Step 5: Inspect Pipeline Results

```bash
ls shared/results/
```

You should see JSON result files for each transaction:

```
TXN001_result.json   TXN004_result.json   TXN007_rejected.json
TXN002_result.json   TXN005_result.json   TXN008_result.json
TXN003_result.json   TXN006_rejected.json pipeline_summary.json
```

View a single result:

```bash
cat shared/results/TXN001_result.json
```

View the pipeline summary:

```bash
cat shared/results/pipeline_summary.json
```

---

## Step 6: Run the Test Suite

```bash
pytest tests/ -v
```

**Expected output (abbreviated):**
```
tests/test_transaction_validator.py::test_valid_usd_transaction PASSED
tests/test_fraud_detector.py::test_high_value_transaction PASSED
tests/test_settlement_processor.py::test_fee_calculation PASSED
tests/test_integration.py::test_full_pipeline_8_transactions PASSED
...
xx passed in x.xxs
```

---

## Step 7: Check Test Coverage

```bash
pytest --cov=agents --cov-report=term-missing tests/
```

**Expected output:**
```
----------- coverage: platform darwin, python 3.x -----------
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
agents/base_agent.py                     67      3    96%
agents/transaction_validator.py         216     12    94%
agents/fraud_detector.py                159      8    95%
agents/settlement_processor.py          232     11    95%
---------------------------------------------------------
TOTAL                                   674     34    95%
```

Coverage must be ≥ 80% (gate enforced by pre-push hook).

---

## Step 8: Start the MCP Server

The MCP server exposes pipeline results as tools that can be queried by Claude or any MCP client.

```bash
python3 mcp/server.py
```

Or via the MCP configuration:

```bash
# The server is pre-configured in mcp.json
# Claude Code will start it automatically when mcp.json is present
```

**Available MCP tools:**
- `get_transaction_status(transaction_id)` — get final status for a specific TXN
- `list_pipeline_results()` — summarise all processed transactions
- `get_pipeline_stats()` — counts by settlement status

**Example query (after pipeline run):**
```
get_transaction_status("TXN001")
# Returns: { "status": "settled", "fraud_risk_level": "LOW", ... }
```

---

## Step 9: Use Slash Commands (Claude Code)

If you have Claude Code installed, these slash commands are available:

```bash
/write-spec              # Generate specification.md from sample-transactions.json
/run-pipeline            # Run the full pipeline end-to-end
/validate-transactions   # Dry-run validation only (no fraud or settlement)
```

To run a slash command:
1. Open this project in Claude Code
2. Type the slash command in the Claude prompt
3. Claude reads the corresponding `.claude/commands/*.md` file and executes the steps

---

## Step 10: Re-run the Pipeline (Clean Start)

To process transactions from scratch (clearing previous results):

```bash
python3 integrator.py --reset
```

This cleans all `shared/` directories and then runs the pipeline in one command.

You can also clean without re-running:

```bash
python3 integrator.py --clean
```

Or manually clear the shared directories:

```bash
rm -rf shared/input/* shared/processing/* shared/output/* shared/results/*
python3 integrator.py
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'fastmcp'`
Install the dependency:
```bash
pip install fastmcp
```

### `FileNotFoundError: sample-transactions.json`
Make sure you are running commands from the `homework-6/` directory:
```bash
cd /path/to/AI-Coding-Partner-Homework/homework-6
```

### `pytest: command not found`
Install pytest:
```bash
pip install pytest pytest-cov
```

### Coverage below 80% blocks git push
The pre-push hook in `.claude/settings.json` runs `bash scripts/check-coverage.sh` before every push. If coverage is below 80%, the push is blocked. Fix by adding tests or checking which lines are uncovered:
```bash
pytest --cov=agents --cov-report=term-missing tests/
```

### `shared/results/` is empty after pipeline run
Check for errors in the integrator output. The most common cause is a missing or malformed `sample-transactions.json`. Verify it contains a JSON array of 8 objects with `transaction_id`, `amount`, `currency`, and `account_number` fields.

### MCP server port conflict
If `mcp/server.py` fails to start due to a port conflict, check `mcp.json` for the configured port and ensure no other process is using it:
```bash
lsof -i :<port>
```

---

## Expected Transaction Outcomes

| TXN ID | Amount | Currency | Expected Outcome |
|--------|--------|----------|-----------------|
| TXN001 | ~$1,500 | USD | settled, LOW risk |
| TXN002 | $25,000 | USD | settled_with_review, MEDIUM risk |
| TXN003 | ~$500 | EUR | settled, LOW risk |
| TXN004 | ~$3,000 | USD | settled, MEDIUM risk (unusual hour) |
| TXN005 | $75,000 | USD | held_for_review, HIGH risk |
| TXN006 | any | XYZ | **rejected** (INVALID_CURRENCY) |
| TXN007 | -$100 | USD | **rejected** (INVALID_AMOUNT) |
| TXN008 | ~$800 | GBP | settled, LOW risk |