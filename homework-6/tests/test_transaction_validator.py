"""Tests for agents/transaction_validator.py."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.transaction_validator import TransactionValidator


@pytest.fixture
def validator():
    return TransactionValidator()


def make_message(data):
    return {"data": dict(data)}


VALID_DATA = {
    "transaction_id": "TXN001",
    "timestamp": "2026-03-16T09:00:00Z",
    "source_account": "ACC-1001",
    "destination_account": "ACC-2001",
    "amount": "1500.00",
    "currency": "USD",
    "transaction_type": "transfer",
}


class TestValidationHappyPath:
    def test_valid_transaction_status(self, validator):
        result = validator.process_message(make_message(VALID_DATA))
        assert result["data"]["status"] == "validated"

    def test_validated_fields_added(self, validator):
        result = validator.process_message(make_message(VALID_DATA))
        data = result["data"]
        assert "validated_at" in data
        assert data["validated_by"] == "transaction_validator"

    def test_target_agent_is_fraud_detector(self, validator):
        result = validator.process_message(make_message(VALID_DATA))
        assert result["target_agent"] == "fraud_detector"

    def test_all_valid_currencies(self, validator):
        for currency in ("USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"):
            data = {**VALID_DATA, "currency": currency, "transaction_id": f"T-{currency}"}
            result = validator.process_message(make_message(data))
            assert result["data"]["status"] == "validated"


class TestMissingFieldRejection:
    @pytest.mark.parametrize("field", [
        "transaction_id", "amount", "currency",
        "source_account", "destination_account", "timestamp", "transaction_type",
    ])
    def test_missing_field_rejected(self, validator, field):
        data = dict(VALID_DATA)
        del data[field]
        result = validator.process_message(make_message(data))
        assert result["data"]["status"] == "rejected"
        assert f"MISSING_FIELD:{field}" in result["data"]["rejection_reason"]

    @pytest.mark.parametrize("field", ["transaction_id", "currency"])
    def test_empty_string_field_rejected(self, validator, field):
        data = {**VALID_DATA, field: "   "}
        result = validator.process_message(make_message(data))
        assert result["data"]["status"] == "rejected"


class TestAmountValidation:
    def test_negative_amount_rejected(self, validator):
        data = {**VALID_DATA, "transaction_id": "TXN007", "amount": "-100.00"}
        result = validator.process_message(make_message(data))
        assert result["data"]["rejection_reason"] == "INVALID_AMOUNT"

    def test_zero_amount_rejected(self, validator):
        data = {**VALID_DATA, "amount": "0.00"}
        result = validator.process_message(make_message(data))
        assert result["data"]["rejection_reason"] == "INVALID_AMOUNT"

    def test_non_numeric_amount_rejected(self, validator):
        data = {**VALID_DATA, "amount": "abc"}
        result = validator.process_message(make_message(data))
        assert result["data"]["rejection_reason"] == "INVALID_AMOUNT"

    def test_decimal_amount_valid(self, validator):
        data = {**VALID_DATA, "amount": "9999.99"}
        result = validator.process_message(make_message(data))
        assert result["data"]["status"] == "validated"

    def test_small_positive_amount_valid(self, validator):
        data = {**VALID_DATA, "amount": "0.01"}
        result = validator.process_message(make_message(data))
        assert result["data"]["status"] == "validated"


class TestCurrencyValidation:
    def test_invalid_currency_rejected(self, validator):
        data = {**VALID_DATA, "transaction_id": "TXN006", "currency": "XYZ"}
        result = validator.process_message(make_message(data))
        assert result["data"]["rejection_reason"] == "INVALID_CURRENCY"

    def test_lowercase_currency_rejected(self, validator):
        data = {**VALID_DATA, "currency": "usd"}
        result = validator.process_message(make_message(data))
        assert result["data"]["rejection_reason"] == "INVALID_CURRENCY"


class TestTimestampValidation:
    def test_invalid_timestamp_rejected(self, validator):
        data = {**VALID_DATA, "timestamp": "not-a-date"}
        result = validator.process_message(make_message(data))
        assert result["data"]["rejection_reason"] == "INVALID_TIMESTAMP"

    def test_valid_timestamp_with_z(self, validator):
        data = {**VALID_DATA, "timestamp": "2026-01-01T00:00:00Z"}
        result = validator.process_message(make_message(data))
        assert result["data"]["status"] == "validated"

    def test_valid_timestamp_with_offset(self, validator):
        data = {**VALID_DATA, "timestamp": "2026-01-01T12:00:00+05:30"}
        result = validator.process_message(make_message(data))
        assert result["data"]["status"] == "validated"


class TestRejectionEnvelope:
    def test_rejected_envelope_has_rejection_fields(self, validator):
        data = {**VALID_DATA, "currency": "XYZ"}
        result = validator.process_message(make_message(data))
        d = result["data"]
        assert d["status"] == "rejected"
        assert "rejection_reason" in d
        assert "rejected_at" in d
        assert d["rejected_by"] == "transaction_validator"

    def test_rejected_message_type(self, validator):
        data = {**VALID_DATA, "currency": "XYZ"}
        result = validator.process_message(make_message(data))
        assert result["message_type"] == "rejection"


class TestFileProcessing:
    def test_valid_file_written_to_output(self, validator, tmp_path, monkeypatch):
        # Patch shared directory constants
        import agents.transaction_validator as tv_module
        monkeypatch.setattr(tv_module, "SHARED_INPUT", str(tmp_path / "input"))
        monkeypatch.setattr(tv_module, "SHARED_PROCESSING", str(tmp_path / "processing"))
        monkeypatch.setattr(tv_module, "SHARED_OUTPUT", str(tmp_path / "output"))
        monkeypatch.setattr(tv_module, "SHARED_RESULTS", str(tmp_path / "results"))

        # Write an input file
        (tmp_path / "input").mkdir(parents=True)
        envelope = {
            "message_id": "m1",
            "timestamp": "2026-01-01T00:00:00Z",
            "source_agent": "integrator",
            "target_agent": "transaction_validator",
            "message_type": "transaction",
            "data": dict(VALID_DATA),
        }
        input_file = tmp_path / "input" / "TXN001_input.json"
        input_file.write_text(json.dumps(envelope))

        validator.process_input_directory()

        output_files = list((tmp_path / "output").glob("*.json"))
        assert len(output_files) == 1
        assert "TXN001" in output_files[0].name

    def test_invalid_file_written_to_results(self, validator, tmp_path, monkeypatch):
        import agents.transaction_validator as tv_module
        monkeypatch.setattr(tv_module, "SHARED_INPUT", str(tmp_path / "input"))
        monkeypatch.setattr(tv_module, "SHARED_PROCESSING", str(tmp_path / "processing"))
        monkeypatch.setattr(tv_module, "SHARED_OUTPUT", str(tmp_path / "output"))
        monkeypatch.setattr(tv_module, "SHARED_RESULTS", str(tmp_path / "results"))

        (tmp_path / "input").mkdir(parents=True)
        bad_data = {**VALID_DATA, "transaction_id": "TXN006", "currency": "XYZ"}
        envelope = {
            "message_id": "m2",
            "timestamp": "2026-01-01T00:00:00Z",
            "source_agent": "integrator",
            "target_agent": "transaction_validator",
            "message_type": "transaction",
            "data": bad_data,
        }
        (tmp_path / "input" / "TXN006_input.json").write_text(json.dumps(envelope))

        validator.process_input_directory()

        result_files = list((tmp_path / "results").glob("*.json"))
        assert len(result_files) == 1
        assert "rejected" in result_files[0].name

    def test_empty_input_directory_no_error(self, validator, tmp_path, monkeypatch):
        import agents.transaction_validator as tv_module
        monkeypatch.setattr(tv_module, "SHARED_INPUT", str(tmp_path / "input"))
        monkeypatch.setattr(tv_module, "SHARED_PROCESSING", str(tmp_path / "processing"))
        monkeypatch.setattr(tv_module, "SHARED_OUTPUT", str(tmp_path / "output"))
        monkeypatch.setattr(tv_module, "SHARED_RESULTS", str(tmp_path / "results"))

        (tmp_path / "input").mkdir(parents=True)
        # Should not raise
        validator.process_input_directory()

    def test_missing_input_directory_no_crash(self, validator, tmp_path, monkeypatch):
        import agents.transaction_validator as tv_module
        monkeypatch.setattr(tv_module, "SHARED_INPUT", str(tmp_path / "nonexistent"))
        monkeypatch.setattr(tv_module, "SHARED_PROCESSING", str(tmp_path / "processing"))
        monkeypatch.setattr(tv_module, "SHARED_OUTPUT", str(tmp_path / "output"))
        monkeypatch.setattr(tv_module, "SHARED_RESULTS", str(tmp_path / "results"))
        validator.process_input_directory()


class TestDryRun:
    def test_dry_run_prints_summary(self, tmp_path, capsys):
        import agents.transaction_validator as tv_module
        from agents.transaction_validator import _dry_run

        transactions = [dict(VALID_DATA), {**VALID_DATA, "transaction_id": "TXN006", "currency": "XYZ"}]
        sample = tmp_path / "sample.json"
        sample.write_text(json.dumps(transactions))

        _dry_run(str(sample))

        captured = capsys.readouterr()
        assert "TXN001" in captured.out
        assert "TXN006" in captured.out
        assert "Valid: 1" in captured.out
        assert "Invalid: 1" in captured.out