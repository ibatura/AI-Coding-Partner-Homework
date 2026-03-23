# Task 2.4 — Integrator / Orchestrator (Python Code Output)

## Overview
The Integrator is the **entry point** for the pipeline. It sets up directories, loads sample transactions, creates message envelopes, feeds them to agents in sequence, and monitors completion.

**Note**: This file describes the **Python code** that the Code Generation sub-agent (`agents/code_generation_agent.md`) produces.

## Step 1: Ensure the Sub-Agent MD File Exists
**Prerequisite**: `agents/code_generation_agent.md` must already exist (from Task 2, Step 1).

## Step 2: Create the Python Code File
**Output file**: `integrator.py` in the project root
- This is a standalone script, not an agent class
- Runnable via: `python integrator.py`

---

## Step 3: Implement Directory Setup

On startup, the integrator must:
1. Create `shared/` directory structure if it doesn't exist:
   - `shared/input/`
   - `shared/processing/`
   - `shared/output/`
   - `shared/results/`
2. **Clear** all `shared/` directories (remove any existing files) for a clean run
3. Log the setup step

---

## Step 4: Load and Prepare Transactions

1. Read `sample-transactions.json`
2. For each transaction, create a standard message envelope:
   ```json
   {
     "message_id": "<uuid4>",
     "timestamp": "<current ISO-8601>",
     "source_agent": "integrator",
     "target_agent": "transaction_validator",
     "message_type": "transaction",
     "data": { <raw transaction data> }
   }
   ```
3. Write each envelope as a JSON file to `shared/input/`
4. Filename format: `{transaction_id}_input.json`

---

## Step 5: Orchestrate Agent Pipeline

Run agents **sequentially** in order:

1. **Transaction Validator**:
   - Instantiate `TransactionValidator`
   - Process all files in `shared/input/`
   - Valid → `shared/output/`, Rejected → `shared/results/`

2. **Fraud Detector**:
   - Instantiate `FraudDetector`
   - Process all `*_validated.json` files in `shared/output/`
   - Scored → `shared/output/` (as `*_scored.json`)

3. **Settlement Processor**:
   - Instantiate `SettlementProcessor`
   - Process all `*_scored.json` files in `shared/output/`
   - Results → `shared/results/`

After all agents complete, trigger the pipeline summary generation.

---

## Step 6: Print Run Summary

After pipeline completion, print to stdout:
- Total transactions loaded
- Validated / rejected counts
- Risk level distribution (LOW / MEDIUM / HIGH)
- Settlement status distribution (settled / settled_with_review / held_for_review / rejected)
- Total fees collected
- List of rejected transactions with reasons
- Path to results directory

---

## Step 7: Error Handling

- Wrap each agent step in try/except
- If an agent crashes on a single transaction, log the error and continue with remaining transactions
- If an agent module fails to import, log error and abort with meaningful message
- If `sample-transactions.json` is missing, exit with clear error message
- Return exit code 0 on success, 1 on any failures

---

## Step 8: CLI Arguments (optional but recommended)

Support optional CLI flags:
- `--input <path>` — custom input file (default: `sample-transactions.json`)
- `--verbose` — enable debug-level logging
- `--clean` — clean `shared/` directories without running pipeline

---

## Files Produced
- `integrator.py` (Python code, output of the sub-agent)

## Dependencies
- `agents/code_generation_agent.md` (the sub-agent that generates this code)
- `agents/base_agent.py`
- `agents/transaction_validator.py` (subtask 2.1)
- `agents/fraud_detector.py` (subtask 2.2)
- `agents/settlement_processor.py` (subtask 2.3)
- `sample-transactions.json`

## Feeds Into
- Task 3 (`/run-pipeline` skill invokes this)
- Task 4 (MCP server reads results)
- Task 5 (integration tests run this)
