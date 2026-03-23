"""Integrator — entry point and orchestrator for the banking pipeline.

Sets up directories, loads sample transactions, creates message envelopes,
and runs agents sequentially: Validator → Fraud Detector → Settlement Processor.
"""

import argparse
import json
import logging
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SHARED_DIRS = [
    "shared/input",
    "shared/processing",
    "shared/output",
    "shared/results",
]

logging.basicConfig(
    format="%(asctime)s | integrator | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("integrator")


def setup_directories(clean: bool = True) -> None:
    """Create shared/ directory structure, optionally clearing existing files."""
    for d in SHARED_DIRS:
        path = Path(d)
        if clean and path.exists():
            for f in path.glob("*"):
                if f.is_file():
                    try:
                        f.unlink()
                    except PermissionError:
                        logger.warning("Could not remove %s (permission denied), skipping", f)
        path.mkdir(parents=True, exist_ok=True)
    logger.info("Shared directories ready (clean=%s)", clean)


def load_transactions(input_path: str) -> list[dict]:
    """Read transactions from JSON file."""
    path = Path(input_path)
    if not path.exists():
        logger.error("Input file not found: %s", input_path)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_input_envelopes(transactions: list[dict]) -> int:
    """Wrap each transaction in a message envelope and write to shared/input/."""
    count = 0
    for txn in transactions:
        envelope = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_agent": "integrator",
            "target_agent": "transaction_validator",
            "message_type": "transaction",
            "data": txn,
        }
        transaction_id = txn.get("transaction_id", str(uuid.uuid4()))
        out_path = Path("shared/input") / f"{transaction_id}_input.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=2)
        count += 1
    logger.info("Wrote %d transaction envelopes to shared/input/", count)
    return count


def run_pipeline(verbose: bool = False) -> bool:
    """Run all three pipeline agents in sequence. Returns True on full success."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    success = True

    # Step 1 — Transaction Validator
    try:
        from agents.transaction_validator import TransactionValidator
        logger.info("--- Stage 1: Transaction Validator ---")
        validator = TransactionValidator()
        validator.process_input_directory()
    except ImportError as e:
        logger.error("Failed to import TransactionValidator: %s", e)
        return False
    except Exception as e:
        logger.error("TransactionValidator failed: %s", e)
        success = False

    # Step 2 — Fraud Detector
    try:
        from agents.fraud_detector import FraudDetector
        logger.info("--- Stage 2: Fraud Detector ---")
        detector = FraudDetector()
        detector.process_output_directory()
    except ImportError as e:
        logger.error("Failed to import FraudDetector: %s", e)
        return False
    except Exception as e:
        logger.error("FraudDetector failed: %s", e)
        success = False

    # Step 3 — Settlement Processor
    try:
        from agents.settlement_processor import SettlementProcessor
        logger.info("--- Stage 3: Settlement Processor ---")
        processor = SettlementProcessor()
        results = processor.process_output_directory()
        processor.write_pipeline_summary(results)
    except ImportError as e:
        logger.error("Failed to import SettlementProcessor: %s", e)
        return False
    except Exception as e:
        logger.error("SettlementProcessor failed: %s", e)
        success = False

    return success


def print_run_summary() -> None:
    """Read pipeline_summary.json and print a human-readable report to stdout."""
    summary_path = Path("shared/results/pipeline_summary.json")
    if not summary_path.exists():
        print("\n[!] No pipeline summary found.")
        return

    with open(summary_path, "r", encoding="utf-8") as f:
        s = json.load(f)

    print("\n" + "=" * 65)
    print("PIPELINE RUN SUMMARY")
    print("=" * 65)
    print(f"  Run ID        : {s.get('run_id')}")
    print(f"  Completed at  : {s.get('completed_at')}")
    print(f"  Total loaded  : {s.get('total_transactions')}")
    print()
    print("  Validation:")
    rejected = s.get("rejected", 0)
    validated = s.get("total_transactions", 0) - rejected
    print(f"    Validated   : {validated}")
    print(f"    Rejected    : {rejected}")
    print()
    print("  Risk Distribution:")
    txns = s.get("transactions", [])
    for level in ("LOW", "MEDIUM", "HIGH"):
        count = sum(1 for t in txns if t.get("fraud_risk_level") == level)
        print(f"    {level:<8}    : {count}")
    print()
    print("  Settlement Distribution:")
    for status in ("settled", "settled_with_review", "held_for_review", "rejected"):
        count = s.get(status, 0)
        print(f"    {status:<22}: {count}")
    print()
    print(f"  Total Fees Collected  : ${s.get('total_fees_collected')}")
    print(f"  Total Volume Processed: ${s.get('total_volume_processed')}")
    print()

    rejected_txns = [t for t in txns if t.get("status") == "rejected"]
    if rejected_txns:
        print("  Rejected Transactions:")
        for t in rejected_txns:
            print(f"    {t['transaction_id']}: {t.get('settlement_fee', 'N/A')}")

    print(f"\n  Results directory: shared/results/")
    print("=" * 65 + "\n")


def clean_shared() -> None:
    """Remove all files from shared/ directories without running the pipeline."""
    for d in SHARED_DIRS:
        path = Path(d)
        if path.exists():
            for f in path.glob("*"):
                if f.is_file():
                    try:
                        f.unlink()
                    except PermissionError:
                        logger.warning("Could not remove %s (permission denied), skipping", f)
    logger.info("Cleaned all shared/ directories.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Banking Pipeline Integrator")
    parser.add_argument(
        "--input",
        default="sample-transactions.json",
        help="Path to input transactions JSON file (default: sample-transactions.json)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug-level logging")
    parser.add_argument(
        "--clean", action="store_true", help="Clean shared/ directories and exit"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Clean shared/ directories, then run the pipeline"
    )
    args = parser.parse_args()

    if args.clean:
        clean_shared()
        sys.exit(0)

    if args.reset:
        clean_shared()

    logger.info("=== Banking Pipeline Starting ===")

    setup_directories(clean=True)
    transactions = load_transactions(args.input)
    logger.info("Loaded %d transactions from %s", len(transactions), args.input)

    write_input_envelopes(transactions)
    success = run_pipeline(verbose=args.verbose)
    print_run_summary()

    logger.info("=== Pipeline Complete ===")
    sys.exit(0 if success else 1)
