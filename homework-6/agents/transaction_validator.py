"""Transaction Validator — first agent in the banking pipeline.

Reads raw transactions from shared/input/, validates them against business rules,
and writes validated messages to shared/output/ or rejected messages to shared/results/.
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

# Allow running as a script from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent

VALID_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"}

REQUIRED_FIELDS = [
    "transaction_id",
    "amount",
    "currency",
    "source_account",
    "destination_account",
    "timestamp",
    "transaction_type",
]

SHARED_INPUT = "shared/input"
SHARED_PROCESSING = "shared/processing"
SHARED_OUTPUT = "shared/output"
SHARED_RESULTS = "shared/results"


class TransactionValidator(BaseAgent):
    """Validates incoming transactions and routes them to the fraud detector or rejects them."""

    def __init__(self) -> None:
        super().__init__("transaction_validator")

    def process_message(self, message: dict) -> dict:
        """Validate a transaction message. Returns updated message with validation result."""
        data = message.get("data", {})
        transaction_id = data.get("transaction_id", "UNKNOWN")

        rejection_reason = self._validate(data)

        now = datetime.now(timezone.utc).isoformat()

        if rejection_reason:
            data["status"] = "rejected"
            data["rejection_reason"] = rejection_reason
            data["rejected_at"] = now
            data["rejected_by"] = self.name
            self.logger.info(
                "transaction_id=%s | outcome=rejected | reason=%s | source=%s",
                transaction_id,
                rejection_reason,
                self.mask_pii(data.get("source_account", "")),
            )
            return self.create_message_envelope(data, target_agent="", message_type="rejection")
        else:
            data["status"] = "validated"
            data["validated_at"] = now
            data["validated_by"] = self.name
            self.logger.info(
                "transaction_id=%s | outcome=validated | source=%s | amount=%s %s",
                transaction_id,
                self.mask_pii(data.get("source_account", "")),
                data.get("amount"),
                data.get("currency"),
            )
            return self.create_message_envelope(data, target_agent="fraud_detector")

    def _validate(self, data: dict) -> str | None:
        """Run all validation rules. Returns rejection reason string or None if valid."""
        # Required field checks
        for field in REQUIRED_FIELDS:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                return f"MISSING_FIELD:{field}"

        # Amount validation (using Decimal, never float)
        try:
            amount = Decimal(str(data["amount"]))
        except (InvalidOperation, TypeError):
            return "INVALID_AMOUNT"

        if amount <= 0:
            return "INVALID_AMOUNT"

        # Currency validation
        if data["currency"] not in VALID_CURRENCIES:
            return "INVALID_CURRENCY"

        # Timestamp validation
        try:
            datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return "INVALID_TIMESTAMP"

        return None

    def process_input_directory(self) -> None:
        """Process all message files in shared/input/."""
        input_dir = Path(SHARED_INPUT)
        if not input_dir.exists():
            self.logger.warning("Input directory %s does not exist", SHARED_INPUT)
            return

        files = list(input_dir.glob("*.json"))
        if not files:
            self.logger.info("No messages found in %s", SHARED_INPUT)
            return

        for filepath in files:
            self._process_file(str(filepath))

    def _process_file(self, filepath: str) -> None:
        """Move file to processing, validate, write result, clean up."""
        filename = Path(filepath).name
        processing_path = Path(SHARED_PROCESSING) / filename
        Path(SHARED_PROCESSING).mkdir(parents=True, exist_ok=True)

        shutil.move(filepath, str(processing_path))
        self.logger.info("Processing file: %s", filename)

        try:
            message = self.read_message(str(processing_path))
            result = self.process_message(message)

            data = result.get("data", {})
            transaction_id = data.get("transaction_id", "UNKNOWN")

            if data.get("status") == "rejected":
                output_path = Path(SHARED_RESULTS) / f"{transaction_id}_rejected.json"
                Path(SHARED_RESULTS).mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, default=str)
            else:
                output_path = Path(SHARED_OUTPUT) / f"{transaction_id}_validated.json"
                Path(SHARED_OUTPUT).mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, default=str)

        except Exception as exc:  # noqa: BLE001
            self.logger.error("Failed to process %s: %s", filename, exc)
        finally:
            if processing_path.exists():
                processing_path.unlink()


def _dry_run(sample_path: str) -> None:
    """Validate all transactions from sample file and print summary table without writing files."""
    validator = TransactionValidator()

    with open(sample_path, "r", encoding="utf-8") as f:
        transactions = json.load(f)

    results = []
    for txn in transactions:
        message = {"data": txn}
        result = validator.process_message(message)
        data = result["data"]
        results.append(
            {
                "transaction_id": data.get("transaction_id"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
                "status": data.get("status"),
                "reason": data.get("rejection_reason", ""),
            }
        )

    valid_count = sum(1 for r in results if r["status"] == "validated")
    invalid_count = sum(1 for r in results if r["status"] == "rejected")

    print(f"\n{'=' * 70}")
    print("DRY-RUN VALIDATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"{'TXN ID':<10} {'Amount':>12} {'Currency':<10} {'Result':<12} {'Reason'}")
    print(f"{'-' * 70}")
    for r in results:
        status_icon = "✅" if r["status"] == "validated" else "❌"
        print(
            f"{r['transaction_id']:<10} {str(r['amount']):>12} {r['currency']:<10} "
            f"{status_icon} {r['status']:<10} {r['reason']}"
        )
    print(f"{'-' * 70}")
    print(f"Total: {len(results)} | Valid: {valid_count} | Invalid: {invalid_count}")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transaction Validator Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate sample-transactions.json without writing to shared/ directories",
    )
    parser.add_argument(
        "--sample",
        default="sample-transactions.json",
        help="Path to sample transactions JSON for dry-run mode",
    )
    args = parser.parse_args()

    if args.dry_run:
        _dry_run(args.sample)
    else:
        validator = TransactionValidator()
        validator.process_input_directory()
