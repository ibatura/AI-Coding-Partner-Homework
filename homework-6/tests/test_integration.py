"""End-to-end integration tests for the full banking pipeline."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


SAMPLE_TRANSACTIONS = [
    {
        "transaction_id": "TXN001",
        "timestamp": "2026-03-16T09:00:00Z",
        "source_account": "ACC-1001",
        "destination_account": "ACC-2001",
        "amount": "1500.00",
        "currency": "USD",
        "transaction_type": "transfer",
        "description": "Monthly rent",
        "metadata": {"channel": "online", "country": "US"},
    },
    {
        "transaction_id": "TXN002",
        "timestamp": "2026-03-16T09:15:00Z",
        "source_account": "ACC-1002",
        "destination_account": "ACC-3001",
        "amount": "25000.00",
        "currency": "USD",
        "transaction_type": "wire_transfer",
        "description": "Equipment purchase",
        "metadata": {"channel": "branch", "country": "US"},
    },
    {
        "transaction_id": "TXN003",
        "timestamp": "2026-03-16T09:30:00Z",
        "source_account": "ACC-1003",
        "destination_account": "ACC-9999",
        "amount": "9999.99",
        "currency": "USD",
        "transaction_type": "transfer",
        "description": "Consulting",
        "metadata": {"channel": "online", "country": "US"},
    },
    {
        "transaction_id": "TXN004",
        "timestamp": "2026-03-16T02:47:00Z",
        "source_account": "ACC-1004",
        "destination_account": "ACC-5500",
        "amount": "500.00",
        "currency": "EUR",
        "transaction_type": "transfer",
        "description": "Invoice",
        "metadata": {"channel": "api", "country": "DE"},
    },
    {
        "transaction_id": "TXN005",
        "timestamp": "2026-03-16T10:00:00Z",
        "source_account": "ACC-1005",
        "destination_account": "ACC-6600",
        "amount": "75000.00",
        "currency": "USD",
        "transaction_type": "wire_transfer",
        "description": "Property settlement",
        "metadata": {"channel": "branch", "country": "US"},
    },
    {
        "transaction_id": "TXN006",
        "timestamp": "2026-03-16T10:05:00Z",
        "source_account": "ACC-1006",
        "destination_account": "ACC-7700",
        "amount": "200.00",
        "currency": "XYZ",
        "transaction_type": "transfer",
        "description": "Test payment",
        "metadata": {"channel": "online", "country": "US"},
    },
    {
        "transaction_id": "TXN007",
        "timestamp": "2026-03-16T10:10:00Z",
        "source_account": "ACC-1007",
        "destination_account": "ACC-8800",
        "amount": "-100.00",
        "currency": "GBP",
        "transaction_type": "refund",
        "description": "Refund",
        "metadata": {"channel": "online", "country": "GB"},
    },
    {
        "transaction_id": "TXN008",
        "timestamp": "2026-03-16T10:15:00Z",
        "source_account": "ACC-1008",
        "destination_account": "ACC-9900",
        "amount": "3200.00",
        "currency": "USD",
        "transaction_type": "transfer",
        "description": "Salary advance",
        "metadata": {"channel": "mobile", "country": "US"},
    },
]


@pytest.fixture
def pipeline_dirs(tmp_path):
    """Set up full shared/ structure and return tmp_path root."""
    for sub in ("input", "processing", "output", "results"):
        (tmp_path / "shared" / sub).mkdir(parents=True)
    return tmp_path


@pytest.fixture
def patch_shared(pipeline_dirs, monkeypatch):
    """Patch shared/ directory constants across all agent modules."""
    root = pipeline_dirs

    import agents.transaction_validator as tv
    import agents.fraud_detector as fd
    import agents.settlement_processor as sp

    monkeypatch.setattr(tv, "SHARED_INPUT", str(root / "shared" / "input"))
    monkeypatch.setattr(tv, "SHARED_PROCESSING", str(root / "shared" / "processing"))
    monkeypatch.setattr(tv, "SHARED_OUTPUT", str(root / "shared" / "output"))
    monkeypatch.setattr(tv, "SHARED_RESULTS", str(root / "shared" / "results"))

    monkeypatch.setattr(fd, "SHARED_OUTPUT", str(root / "shared" / "output"))
    monkeypatch.setattr(fd, "SHARED_PROCESSING", str(root / "shared" / "processing"))

    monkeypatch.setattr(sp, "SHARED_OUTPUT", str(root / "shared" / "output"))
    monkeypatch.setattr(sp, "SHARED_PROCESSING", str(root / "shared" / "processing"))
    monkeypatch.setattr(sp, "SHARED_RESULTS", str(root / "shared" / "results"))

    return root


def write_input_envelopes(transactions, input_dir):
    """Write envelopes to input_dir."""
    import uuid
    from datetime import datetime, timezone

    for txn in transactions:
        envelope = {
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_agent": "integrator",
            "target_agent": "transaction_validator",
            "message_type": "transaction",
            "data": txn,
        }
        path = Path(input_dir) / f"{txn['transaction_id']}_input.json"
        path.write_text(json.dumps(envelope))


class TestFullPipeline:
    def test_all_8_transactions_produce_result_files(self, patch_shared):
        root = patch_shared
        from agents.transaction_validator import TransactionValidator
        from agents.fraud_detector import FraudDetector
        from agents.settlement_processor import SettlementProcessor

        write_input_envelopes(SAMPLE_TRANSACTIONS, root / "shared" / "input")

        TransactionValidator().process_input_directory()
        FraudDetector().process_output_directory()
        processor = SettlementProcessor()
        results = processor.process_output_directory()
        processor.write_pipeline_summary(results)

        result_files = [
            f for f in (root / "shared" / "results").glob("*.json")
            if f.name != "pipeline_summary.json"
        ]
        assert len(result_files) == 8

    def test_txn006_and_txn007_rejected(self, patch_shared):
        root = patch_shared
        from agents.transaction_validator import TransactionValidator

        write_input_envelopes(SAMPLE_TRANSACTIONS, root / "shared" / "input")
        TransactionValidator().process_input_directory()

        rejected = list((root / "shared" / "results").glob("*_rejected.json"))
        rejected_ids = {f.name for f in rejected}
        assert any("TXN006" in n for n in rejected_ids)
        assert any("TXN007" in n for n in rejected_ids)

    def test_six_transactions_validated(self, patch_shared):
        root = patch_shared
        from agents.transaction_validator import TransactionValidator

        write_input_envelopes(SAMPLE_TRANSACTIONS, root / "shared" / "input")
        TransactionValidator().process_input_directory()

        validated = list((root / "shared" / "output").glob("*_validated.json"))
        assert len(validated) == 6

    def test_txn005_held_for_review(self, patch_shared):
        root = patch_shared
        from agents.transaction_validator import TransactionValidator
        from agents.fraud_detector import FraudDetector
        from agents.settlement_processor import SettlementProcessor

        write_input_envelopes(SAMPLE_TRANSACTIONS, root / "shared" / "input")
        TransactionValidator().process_input_directory()
        FraudDetector().process_output_directory()
        SettlementProcessor().process_output_directory()

        txn5_result = root / "shared" / "results" / "TXN005_result.json"
        assert txn5_result.exists()
        data = json.loads(txn5_result.read_text())["data"]
        assert data["settlement_status"] == "held_for_review"

    def test_pipeline_summary_counts(self, patch_shared):
        root = patch_shared
        from agents.transaction_validator import TransactionValidator
        from agents.fraud_detector import FraudDetector
        from agents.settlement_processor import SettlementProcessor

        write_input_envelopes(SAMPLE_TRANSACTIONS, root / "shared" / "input")
        TransactionValidator().process_input_directory()
        FraudDetector().process_output_directory()
        processor = SettlementProcessor()
        results = processor.process_output_directory()
        processor.write_pipeline_summary(results)

        summary = json.loads(
            (root / "shared" / "results" / "pipeline_summary.json").read_text()
        )
        assert summary["total_transactions"] == 8
        assert summary["rejected"] == 2

    def test_processing_dir_empty_after_pipeline(self, patch_shared):
        root = patch_shared
        from agents.transaction_validator import TransactionValidator
        from agents.fraud_detector import FraudDetector
        from agents.settlement_processor import SettlementProcessor

        write_input_envelopes(SAMPLE_TRANSACTIONS, root / "shared" / "input")
        TransactionValidator().process_input_directory()
        FraudDetector().process_output_directory()
        SettlementProcessor().process_output_directory()

        processing_files = list((root / "shared" / "processing").glob("*.json"))
        assert processing_files == []