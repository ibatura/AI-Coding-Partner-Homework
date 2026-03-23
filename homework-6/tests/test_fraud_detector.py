"""Tests for agents/fraud_detector.py."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.fraud_detector import FraudDetector


@pytest.fixture
def detector():
    return FraudDetector()


def make_validated_message(data):
    return {
        "message_id": "test-id",
        "timestamp": "2026-03-16T09:00:00Z",
        "source_agent": "transaction_validator",
        "target_agent": "fraud_detector",
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
    "metadata": {"channel": "online", "country": "US"},
}


class TestRiskScoring:
    def test_low_amount_us_daytime_score_zero(self, detector):
        result = detector.process_message(make_validated_message(BASE_DATA))
        assert result["data"]["fraud_risk_score"] == 0
        assert result["data"]["fraud_risk_level"] == "LOW"

    def test_high_value_adds_three(self, detector):
        data = {**BASE_DATA, "amount": "25000.00"}
        result = detector.process_message(make_validated_message(data))
        score = result["data"]["fraud_risk_score"]
        assert score >= 3
        assert "HIGH_VALUE" in result["data"]["fraud_flags"]

    def test_very_high_value_adds_seven(self, detector):
        # >50K adds +3 + +4 = 7
        data = {**BASE_DATA, "amount": "75000.00"}
        result = detector.process_message(make_validated_message(data))
        score = result["data"]["fraud_risk_score"]
        assert score >= 7
        assert "VERY_HIGH_VALUE" in result["data"]["fraud_flags"]
        assert "HIGH_VALUE" in result["data"]["fraud_flags"]

    def test_unusual_hour_adds_two(self, detector):
        # hour=3 (03:00 UTC) is in unusual range
        data = {**BASE_DATA, "timestamp": "2026-03-16T03:00:00Z", "amount": "100.00"}
        result = detector.process_message(make_validated_message(data))
        assert "UNUSUAL_HOUR" in result["data"]["fraud_flags"]
        assert result["data"]["fraud_risk_score"] >= 2

    def test_unusual_hour_boundary_02(self, detector):
        data = {**BASE_DATA, "timestamp": "2026-03-16T02:00:00Z", "amount": "100.00"}
        result = detector.process_message(make_validated_message(data))
        assert "UNUSUAL_HOUR" in result["data"]["fraud_flags"]

    def test_unusual_hour_boundary_04(self, detector):
        data = {**BASE_DATA, "timestamp": "2026-03-16T04:59:00Z", "amount": "100.00"}
        result = detector.process_message(make_validated_message(data))
        assert "UNUSUAL_HOUR" in result["data"]["fraud_flags"]

    def test_normal_hour_no_flag(self, detector):
        data = {**BASE_DATA, "timestamp": "2026-03-16T09:00:00Z", "amount": "100.00"}
        result = detector.process_message(make_validated_message(data))
        assert "UNUSUAL_HOUR" not in result["data"]["fraud_flags"]

    def test_cross_border_adds_one(self, detector):
        data = {**BASE_DATA, "metadata": {"country": "DE"}}
        result = detector.process_message(make_validated_message(data))
        assert "CROSS_BORDER" in result["data"]["fraud_flags"]
        assert result["data"]["fraud_risk_score"] >= 1

    def test_us_no_cross_border_flag(self, detector):
        result = detector.process_message(make_validated_message(BASE_DATA))
        assert "CROSS_BORDER" not in result["data"]["fraud_flags"]

    def test_score_capped_at_ten(self, detector):
        # >50K + unusual hour + cross border = 7+2+1 = 10
        data = {
            **BASE_DATA,
            "amount": "75000.00",
            "timestamp": "2026-03-16T03:00:00Z",
            "metadata": {"country": "DE"},
        }
        result = detector.process_message(make_validated_message(data))
        assert result["data"]["fraud_risk_score"] <= 10


class TestRiskLevelAssignment:
    def test_score_0_is_low(self, detector):
        assert detector._assign_risk_level(0) == "LOW"

    def test_score_2_is_low(self, detector):
        assert detector._assign_risk_level(2) == "LOW"

    def test_score_3_is_medium(self, detector):
        assert detector._assign_risk_level(3) == "MEDIUM"

    def test_score_6_is_medium(self, detector):
        assert detector._assign_risk_level(6) == "MEDIUM"

    def test_score_7_is_high(self, detector):
        assert detector._assign_risk_level(7) == "HIGH"

    def test_score_10_is_high(self, detector):
        assert detector._assign_risk_level(10) == "HIGH"


class TestEnvelopeOutput:
    def test_target_agent_is_settlement_processor(self, detector):
        result = detector.process_message(make_validated_message(BASE_DATA))
        assert result["target_agent"] == "settlement_processor"

    def test_fraud_fields_added(self, detector):
        result = detector.process_message(make_validated_message(BASE_DATA))
        data = result["data"]
        assert "fraud_risk_score" in data
        assert "fraud_risk_level" in data
        assert "fraud_flags" in data
        assert "fraud_checked_at" in data
        assert data["fraud_checked_by"] == "fraud_detector"

    def test_unusual_hour_bool_field(self, detector):
        data = {**BASE_DATA, "timestamp": "2026-03-16T03:00:00Z"}
        result = detector.process_message(make_validated_message(data))
        assert result["data"]["unusual_hour"] is True

    def test_cross_border_bool_field(self, detector):
        data = {**BASE_DATA, "metadata": {"country": "FR"}}
        result = detector.process_message(make_validated_message(data))
        assert result["data"]["cross_border"] is True

    def test_no_metadata_no_crash(self, detector):
        data = {k: v for k, v in BASE_DATA.items() if k != "metadata"}
        result = detector.process_message(make_validated_message(data))
        # Missing metadata defaults to US (no cross-border)
        assert "CROSS_BORDER" not in result["data"]["fraud_flags"]

    def test_malformed_amount_no_crash(self, detector):
        data = {**BASE_DATA, "amount": "bad"}
        result = detector.process_message(make_validated_message(data))
        assert "fraud_risk_score" in result["data"]

    def test_malformed_timestamp_no_crash(self, detector):
        data = {**BASE_DATA, "timestamp": "not-a-date"}
        result = detector.process_message(make_validated_message(data))
        assert "fraud_risk_score" in result["data"]


class TestSampleDataExpectations:
    """Verify scoring matches expected table from task2.2.md."""

    def test_txn001_score_0_low(self, detector):
        data = {**BASE_DATA, "amount": "1500.00", "timestamp": "2026-03-16T09:00:00Z",
                "metadata": {"country": "US"}}
        result = detector.process_message(make_validated_message(data))
        assert result["data"]["fraud_risk_score"] == 0
        assert result["data"]["fraud_risk_level"] == "LOW"

    def test_txn002_score_3_medium(self, detector):
        data = {**BASE_DATA, "transaction_id": "TXN002", "amount": "25000.00",
                "timestamp": "2026-03-16T09:15:00Z", "metadata": {"country": "US"}}
        result = detector.process_message(make_validated_message(data))
        assert result["data"]["fraud_risk_score"] == 3
        assert result["data"]["fraud_risk_level"] == "MEDIUM"

    def test_txn004_score_3_medium_unusual_crossborder(self, detector):
        data = {**BASE_DATA, "transaction_id": "TXN004", "amount": "500.00",
                "timestamp": "2026-03-16T02:47:00Z", "metadata": {"country": "DE"}}
        result = detector.process_message(make_validated_message(data))
        assert result["data"]["fraud_risk_score"] == 3
        assert result["data"]["fraud_risk_level"] == "MEDIUM"
        assert "UNUSUAL_HOUR" in result["data"]["fraud_flags"]
        assert "CROSS_BORDER" in result["data"]["fraud_flags"]

    def test_txn005_score_7_high(self, detector):
        data = {**BASE_DATA, "transaction_id": "TXN005", "amount": "75000.00",
                "timestamp": "2026-03-16T10:00:00Z", "metadata": {"country": "US"}}
        result = detector.process_message(make_validated_message(data))
        assert result["data"]["fraud_risk_score"] == 7
        assert result["data"]["fraud_risk_level"] == "HIGH"


class TestFileProcessing:
    def test_process_output_directory(self, detector, tmp_path, monkeypatch):
        import agents.fraud_detector as fd_module
        monkeypatch.setattr(fd_module, "SHARED_OUTPUT", str(tmp_path / "output"))
        monkeypatch.setattr(fd_module, "SHARED_PROCESSING", str(tmp_path / "processing"))

        (tmp_path / "output").mkdir(parents=True)
        (tmp_path / "processing").mkdir(parents=True)

        envelope = {
            "message_id": "m1",
            "timestamp": "2026-01-01T00:00:00Z",
            "source_agent": "transaction_validator",
            "target_agent": "fraud_detector",
            "message_type": "transaction",
            "data": dict(BASE_DATA),
        }
        (tmp_path / "output" / "TXN001_validated.json").write_text(json.dumps(envelope))

        detector.process_output_directory()

        scored = list((tmp_path / "output").glob("*_scored.json"))
        assert len(scored) == 1

    def test_missing_output_directory_no_crash(self, detector, tmp_path, monkeypatch):
        import agents.fraud_detector as fd_module
        monkeypatch.setattr(fd_module, "SHARED_OUTPUT", str(tmp_path / "nonexistent"))
        monkeypatch.setattr(fd_module, "SHARED_PROCESSING", str(tmp_path / "processing"))
        detector.process_output_directory()