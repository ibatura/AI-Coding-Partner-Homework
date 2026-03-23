"""Fraud Detector — second agent in the banking pipeline.

Reads validated transactions from shared/output/, calculates a fraud risk score
(0–10 scale), assigns a risk level, and passes them to the settlement processor.
"""

import json
import shutil
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent

SHARED_OUTPUT = "shared/output"
SHARED_PROCESSING = "shared/processing"

HIGH_VALUE_THRESHOLD = Decimal("10000")
VERY_HIGH_VALUE_THRESHOLD = Decimal("50000")
UNUSUAL_HOUR_START = 2  # 02:00 UTC inclusive
UNUSUAL_HOUR_END = 4    # 04:59 UTC inclusive


class FraudDetector(BaseAgent):
    """Scores fraud risk for validated transactions."""

    def __init__(self) -> None:
        super().__init__("fraud_detector")

    def process_message(self, message: dict) -> dict:
        """Score a validated transaction for fraud risk. Returns updated message."""
        data = message.get("data", {})
        transaction_id = data.get("transaction_id", "UNKNOWN")

        score, flags = self._calculate_risk(data)
        risk_level = self._assign_risk_level(score)

        now = datetime.now(timezone.utc).isoformat()
        data["fraud_risk_score"] = score
        data["fraud_risk_level"] = risk_level
        data["fraud_flags"] = flags
        data["fraud_checked_at"] = now
        data["fraud_checked_by"] = self.name
        data["unusual_hour"] = "UNUSUAL_HOUR" in flags
        data["cross_border"] = "CROSS_BORDER" in flags

        log_msg = (
            "transaction_id=%s | score=%d | level=%s | flags=%s | source=%s",
            transaction_id,
            score,
            risk_level,
            flags,
            self.mask_pii(data.get("source_account", "")),
        )
        if risk_level == "HIGH":
            self.logger.warning(*log_msg)
        else:
            self.logger.info(*log_msg)

        return self.create_message_envelope(data, target_agent="settlement_processor")

    def _calculate_risk(self, data: dict) -> tuple[int, list[str]]:
        """Calculate additive fraud risk score and collect triggered flags."""
        score = 0
        flags: list[str] = []

        # Amount-based scoring
        try:
            amount = Decimal(str(data.get("amount", "0")))
        except Exception:
            amount = Decimal("0")

        if amount > HIGH_VALUE_THRESHOLD:
            score += 3
            flags.append("HIGH_VALUE")

        if amount > VERY_HIGH_VALUE_THRESHOLD:
            score += 4
            flags.append("VERY_HIGH_VALUE")

        # Unusual hour scoring (02:00–04:59 UTC inclusive)
        timestamp_str = data.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            hour = dt.hour
            if UNUSUAL_HOUR_START <= hour <= UNUSUAL_HOUR_END:
                score += 2
                flags.append("UNUSUAL_HOUR")
        except (ValueError, AttributeError):
            pass

        # Cross-border scoring
        country = data.get("metadata", {}).get("country", "US")
        if country != "US":
            score += 1
            flags.append("CROSS_BORDER")

        # Cap score at 10
        score = min(score, 10)

        return score, flags

    def _assign_risk_level(self, score: int) -> str:
        """Map numeric score to risk level."""
        if score >= 7:
            return "HIGH"
        if score >= 3:
            return "MEDIUM"
        return "LOW"

    def process_output_directory(self) -> None:
        """Process all *_validated.json files in shared/output/."""
        output_dir = Path(SHARED_OUTPUT)
        if not output_dir.exists():
            self.logger.warning("Output directory %s does not exist", SHARED_OUTPUT)
            return

        files = list(output_dir.glob("*_validated.json"))
        if not files:
            self.logger.info("No validated messages found in %s", SHARED_OUTPUT)
            return

        for filepath in files:
            self._process_file(str(filepath))

    def _process_file(self, filepath: str) -> None:
        """Move file to processing, score it, write result, clean up."""
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

            scored_path = Path(SHARED_OUTPUT) / f"{transaction_id}_scored.json"
            Path(SHARED_OUTPUT).mkdir(parents=True, exist_ok=True)
            with open(scored_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)

        except Exception as exc:  # noqa: BLE001
            self.logger.error("Failed to process %s: %s", filename, exc)
        finally:
            if processing_path.exists():
                processing_path.unlink()


if __name__ == "__main__":
    detector = FraudDetector()
    detector.process_output_directory()
