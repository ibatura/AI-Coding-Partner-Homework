"""Tests for agents/settlement_processor.py."""

import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.settlement_processor import SettlementProcessor


@pytest.fixture
def processor():
    return SettlementProcessor()


def make_scored_message(data):
    return {
        "message_id": "test-id",
        "timestamp": "2026-03-16T09:00:00Z",
        "source_agent": "fraud_detector",
        "target_agent": "settlement_processor",
        "message_type": "transaction",
        "data": dict(data),
    }


BASE_DATA = {
    "transaction_id": "TXN001",
    "timestamp": "2026-03-16T09:00:00Z",
    "source_account": "ACC-1001",
    "destination_account": "ACC-2001",
    "amount": "1500.00",
    "currency": "USD",
    "transaction_type": "transfer",
    "status": "validated",
    "fraud_risk_score": 0,
    "fraud_risk_level": "LOW",
    "fraud_flags": [],
}


class TestFeeCalculation:
    def test_normal_fee_is_0_1_percent(self, processor):
        # 1500 * 0.001 = 1.50
        fee = processor._calculate_fee(Decimal("1500.00"))
        assert fee == Decimal("1.50")

    def test_minimum_fee_applied(self, processor):
        # 10 * 0.001 = 0.01, min is 0.50
        fee = processor._calculate_fee(Decimal("10.00"))
        assert fee == Decimal("0.50")

    def test_maximum_fee_applied(self, processor):
        # 100000 * 0.001 = 100, max is 50.00
        fee = processor._calculate_fee(Decimal("100000.00"))
        assert fee == Decimal("50.00")

    def test_fee_at_exact_min_boundary(self, processor):
        # 500 * 0.001 = 0.50 (exactly at min)
        fee = processor._calculate_fee(Decimal("500.00"))
        assert fee == Decimal("0.50")

    def test_fee_at_exact_max_boundary(self, processor):
        # 50000 * 0.001 = 50.00 (exactly at max)
        fee = processor._calculate_fee(Decimal("50000.00"))
        assert fee == Decimal("50.00")


class TestLowRiskSettlement:
    def test_status_is_settled(self, processor):
        result = processor.process_message(make_scored_message(BASE_DATA))
        assert result["data"]["settlement_status"] == "settled"

    def test_settlement_id_assigned(self, processor):
        result = processor.process_message(make_scored_message(BASE_DATA))
        assert result["data"]["settlement_id"].startswith("STL-")

    def test_fee_and_net_amount_set(self, processor):
        result = processor.process_message(make_scored_message(BASE_DATA))
        data = result["data"]
        fee = Decimal(data["settlement_fee"])
        net = Decimal(data["net_amount"])
        amount = Decimal(data["amount"])
        assert fee > 0
        assert net == amount - fee

    def test_settled_at_set(self, processor):
        result = processor.process_message(make_scored_message(BASE_DATA))
        assert result["data"]["settled_at"] is not None

    def test_pipeline_complete_true(self, processor):
        result = processor.process_message(make_scored_message(BASE_DATA))
        assert result["data"]["pipeline_complete"] is True

    def test_settled_by_is_settlement_processor(self, processor):
        result = processor.process_message(make_scored_message(BASE_DATA))
        assert result["data"]["settled_by"] == "settlement_processor"


class TestMediumRiskSettlement:
    def test_status_is_settled_with_review(self, processor):
        data = {**BASE_DATA, "fraud_risk_level": "MEDIUM"}
        result = processor.process_message(make_scored_message(data))
        assert result["data"]["settlement_status"] == "settled_with_review"

    def test_fee_applied_for_medium(self, processor):
        data = {**BASE_DATA, "fraud_risk_level": "MEDIUM", "amount": "25000.00"}
        result = processor.process_message(make_scored_message(data))
        assert Decimal(result["data"]["settlement_fee"]) == Decimal("25.00")


class TestHighRiskHold:
    def test_status_is_held_for_review(self, processor):
        data = {**BASE_DATA, "fraud_risk_level": "HIGH", "amount": "75000.00"}
        result = processor.process_message(make_scored_message(data))
        assert result["data"]["settlement_status"] == "held_for_review"

    def test_no_fee_for_held(self, processor):
        data = {**BASE_DATA, "fraud_risk_level": "HIGH", "amount": "75000.00"}
        result = processor.process_message(make_scored_message(data))
        assert Decimal(result["data"]["settlement_fee"]) == Decimal("0.00")

    def test_hold_reason_set(self, processor):
        data = {**BASE_DATA, "fraud_risk_level": "HIGH"}
        result = processor.process_message(make_scored_message(data))
        assert result["data"]["hold_reason"] == "HIGH_FRAUD_RISK"

    def test_settled_at_is_none_for_held(self, processor):
        data = {**BASE_DATA, "fraud_risk_level": "HIGH"}
        result = processor.process_message(make_scored_message(data))
        assert result["data"]["settled_at"] is None

    def test_settlement_id_is_none_for_held(self, processor):
        data = {**BASE_DATA, "fraud_risk_level": "HIGH"}
        result = processor.process_message(make_scored_message(data))
        assert result["data"]["settlement_id"] is None

    def test_net_amount_equals_amount_for_held(self, processor):
        data = {**BASE_DATA, "fraud_risk_level": "HIGH", "amount": "75000.00"}
        result = processor.process_message(make_scored_message(data))
        assert result["data"]["net_amount"] == "75000.00"


class TestEnvelopeOutput:
    def test_message_type_is_result(self, processor):
        result = processor.process_message(make_scored_message(BASE_DATA))
        assert result["message_type"] == "result"

    def test_target_agent_empty(self, processor):
        result = processor.process_message(make_scored_message(BASE_DATA))
        assert result["target_agent"] == ""

    def test_malformed_amount_no_crash(self, processor):
        data = {**BASE_DATA, "amount": "bad"}
        result = processor.process_message(make_scored_message(data))
        assert "settlement_status" in result["data"]


class TestFileProcessing:
    def test_process_output_directory(self, processor, tmp_path, monkeypatch):
        import agents.settlement_processor as sp_module
        monkeypatch.setattr(sp_module, "SHARED_OUTPUT", str(tmp_path / "output"))
        monkeypatch.setattr(sp_module, "SHARED_PROCESSING", str(tmp_path / "processing"))
        monkeypatch.setattr(sp_module, "SHARED_RESULTS", str(tmp_path / "results"))

        for sub in ("output", "processing", "results"):
            (tmp_path / sub).mkdir(parents=True)

        envelope = {
            "message_id": "m1",
            "timestamp": "2026-01-01T00:00:00Z",
            "source_agent": "fraud_detector",
            "target_agent": "settlement_processor",
            "message_type": "transaction",
            "data": dict(BASE_DATA),
        }
        (tmp_path / "output" / "TXN001_scored.json").write_text(json.dumps(envelope))

        results = processor.process_output_directory()
        assert len(results) == 1
        result_files = list((tmp_path / "results").glob("*.json"))
        assert len(result_files) == 1

    def test_missing_output_directory_returns_empty(self, processor, tmp_path, monkeypatch):
        import agents.settlement_processor as sp_module
        monkeypatch.setattr(sp_module, "SHARED_OUTPUT", str(tmp_path / "nonexistent"))
        monkeypatch.setattr(sp_module, "SHARED_PROCESSING", str(tmp_path / "processing"))
        monkeypatch.setattr(sp_module, "SHARED_RESULTS", str(tmp_path / "results"))
        assert processor.process_output_directory() == []


class TestPipelineSummary:
    def test_summary_written(self, processor, tmp_path, monkeypatch):
        import agents.settlement_processor as sp_module
        monkeypatch.setattr(sp_module, "SHARED_RESULTS", str(tmp_path / "results"))

        results_dir = tmp_path / "results"
        results_dir.mkdir(parents=True)

        # Write two result files
        for txn_id, status in [("TXN001", "settled"), ("TXN005", "held_for_review")]:
            data = {
                "transaction_id": txn_id,
                "amount": "1000.00",
                "currency": "USD",
                "settlement_status": status,
                "settlement_fee": "1.00" if status == "settled" else "0.00",
                "net_amount": "999.00" if status == "settled" else "1000.00",
                "fraud_risk_level": "LOW" if status == "settled" else "HIGH",
            }
            envelope = {"data": data}
            (results_dir / f"{txn_id}_result.json").write_text(json.dumps(envelope))

        processor.write_pipeline_summary([])

        summary_path = results_dir / "pipeline_summary.json"
        assert summary_path.exists()
        summary = json.loads(summary_path.read_text())
        assert summary["total_transactions"] == 2
        assert summary["settled"] == 1
        assert summary["held_for_review"] == 1