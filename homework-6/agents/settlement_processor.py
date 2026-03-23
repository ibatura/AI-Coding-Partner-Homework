"""Settlement Processor — third and final agent in the banking pipeline.

Reads fraud-scored transactions from shared/output/, applies settlement logic
(fees, holds, approvals), and writes final results to shared/results/.
"""

import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent

SHARED_OUTPUT = "shared/output"
SHARED_PROCESSING = "shared/processing"
SHARED_RESULTS = "shared/results"

FEE_RATE = Decimal("0.001")
FEE_MIN = Decimal("0.50")
FEE_MAX = Decimal("50.00")
ZERO = Decimal("0.00")


class SettlementProcessor(BaseAgent):
    """Settles or holds fraud-scored transactions and writes final results."""

    def __init__(self) -> None:
        super().__init__("settlement_processor")

    def process_message(self, message: dict) -> dict:
        """Apply settlement logic to a scored transaction. Returns final message."""
        data = message.get("data", {})
        transaction_id = data.get("transaction_id", "UNKNOWN")
        risk_level = data.get("fraud_risk_level", "LOW")

        try:
            amount = Decimal(str(data.get("amount", "0")))
        except Exception:
            amount = ZERO

        now = datetime.now(timezone.utc).isoformat()

        if risk_level == "HIGH":
            data["settlement_status"] = "held_for_review"
            data["settlement_id"] = None
            data["settlement_fee"] = str(ZERO)
            data["net_amount"] = str(amount)
            data["hold_reason"] = "HIGH_FRAUD_RISK"
            data["settled_at"] = None
            self.logger.warning(
                "transaction_id=%s | status=held_for_review | risk=HIGH | source=%s",
                transaction_id,
                self.mask_pii(data.get("source_account", "")),
            )
        else:
            fee = self._calculate_fee(amount)
            net = (amount - fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            settlement_id = f"STL-{str(uuid.uuid4())[:8]}"

            if risk_level == "MEDIUM":
                status = "settled_with_review"
            else:
                status = "settled"

            data["settlement_status"] = status
            data["settlement_id"] = settlement_id
            data["settlement_fee"] = str(fee)
            data["net_amount"] = str(net)
            data["settled_at"] = now
            self.logger.info(
                "transaction_id=%s | status=%s | fee=%s | net=%s | source=%s",
                transaction_id,
                status,
                fee,
                net,
                self.mask_pii(data.get("source_account", "")),
            )

        data["settled_by"] = self.name
        data["pipeline_complete"] = True

        return self.create_message_envelope(data, target_agent="", message_type="result")

    def _calculate_fee(self, amount: Decimal) -> Decimal:
        """Calculate transaction fee: 0.1% of amount, min $0.50, max $50.00."""
        fee = (amount * FEE_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return max(min(fee, FEE_MAX), FEE_MIN)

    def process_output_directory(self) -> list[dict]:
        """Process all *_scored.json files in shared/output/. Returns list of result data."""
        output_dir = Path(SHARED_OUTPUT)
        if not output_dir.exists():
            self.logger.warning("Output directory %s does not exist", SHARED_OUTPUT)
            return []

        files = list(output_dir.glob("*_scored.json"))
        if not files:
            self.logger.info("No scored messages found in %s", SHARED_OUTPUT)
            return []

        results = []
        for filepath in files:
            result = self._process_file(str(filepath))
            if result:
                results.append(result)
        return results

    def _process_file(self, filepath: str) -> dict | None:
        """Move file to processing, settle it, write result, clean up."""
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

            result_path = Path(SHARED_RESULTS) / f"{transaction_id}_result.json"
            Path(SHARED_RESULTS).mkdir(parents=True, exist_ok=True)
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)

            return data

        except Exception as exc:  # noqa: BLE001
            self.logger.error("Failed to process %s: %s", filename, exc)
            return None
        finally:
            if processing_path.exists():
                processing_path.unlink()

    def write_pipeline_summary(self, settled_results: list[dict]) -> None:
        """Read all results from shared/results/ and write pipeline_summary.json."""
        results_dir = Path(SHARED_RESULTS)
        Path(SHARED_RESULTS).mkdir(parents=True, exist_ok=True)

        # Gather all result files (exclude the summary itself)
        all_results: list[dict] = []
        for fpath in results_dir.glob("*.json"):
            if fpath.name == "pipeline_summary.json":
                continue
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    envelope = json.load(f)
                all_results.append(envelope.get("data", {}))
            except Exception:
                pass

        counts = {"settled": 0, "settled_with_review": 0, "held_for_review": 0, "rejected": 0}
        total_fees = ZERO
        total_volume = ZERO
        txn_summaries = []

        for d in all_results:
            status = d.get("settlement_status") or d.get("status", "unknown")
            if status in counts:
                counts[status] += 1

            try:
                amount = Decimal(str(d.get("amount", "0")))
                total_volume += amount
            except Exception:
                pass

            try:
                fee = Decimal(str(d.get("settlement_fee", "0")))
                total_fees += fee
            except Exception:
                pass

            txn_summaries.append(
                {
                    "transaction_id": d.get("transaction_id"),
                    "amount": d.get("amount"),
                    "currency": d.get("currency"),
                    "status": status,
                    "settlement_id": d.get("settlement_id"),
                    "settlement_fee": d.get("settlement_fee", "0.00"),
                    "net_amount": d.get("net_amount"),
                    "fraud_risk_level": d.get("fraud_risk_level"),
                }
            )

        summary = {
            "run_id": str(uuid.uuid4()),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "total_transactions": len(all_results),
            "settled": counts["settled"],
            "settled_with_review": counts["settled_with_review"],
            "held_for_review": counts["held_for_review"],
            "rejected": counts["rejected"],
            "total_fees_collected": str(
                total_fees.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "total_volume_processed": str(
                total_volume.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "transactions": txn_summaries,
        }

        summary_path = results_dir / "pipeline_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)

        self.logger.info(
            "Pipeline summary written | total=%d | settled=%d | settled_with_review=%d"
            " | held=%d | rejected=%d | fees=%s | volume=%s",
            summary["total_transactions"],
            summary["settled"],
            summary["settled_with_review"],
            summary["held_for_review"],
            summary["rejected"],
            summary["total_fees_collected"],
            summary["total_volume_processed"],
        )


if __name__ == "__main__":
    processor = SettlementProcessor()
    results = processor.process_output_directory()
    processor.write_pipeline_summary(results)
