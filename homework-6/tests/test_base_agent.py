"""Tests for agents/base_agent.py."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent


class ConcreteAgent(BaseAgent):
    """Minimal concrete subclass for testing abstract BaseAgent."""

    def __init__(self):
        super().__init__("test_agent")

    def process_message(self, message: dict) -> dict:
        return message


@pytest.fixture
def agent():
    return ConcreteAgent()


class TestSetupLogging:
    def test_logger_name(self, agent):
        assert agent.logger.name == "test_agent"

    def test_logger_level_info(self, agent):
        import logging
        assert agent.logger.level == logging.INFO

    def test_no_duplicate_handlers_on_reinstantiation(self):
        a1 = ConcreteAgent()
        handler_count = len(a1.logger.handlers)
        ConcreteAgent()  # second instantiation
        assert len(a1.logger.handlers) == handler_count


class TestMaskPii:
    def test_masks_account_number(self, agent):
        assert agent.mask_pii("ACC-1001") == "ACC-***1"

    def test_masks_last_digit_only(self, agent):
        assert agent.mask_pii("ACC-9876") == "ACC-***6"

    def test_masks_multiple_accounts(self, agent):
        result = agent.mask_pii("from ACC-1001 to ACC-2002")
        assert "ACC-***1" in result
        assert "ACC-***2" in result

    def test_no_account_unchanged(self, agent):
        assert agent.mask_pii("no account here") == "no account here"

    def test_non_string_coerced(self, agent):
        result = agent.mask_pii({"key": "ACC-1234"})
        assert "ACC-***4" in result


class TestCreateMessageEnvelope:
    def test_envelope_keys(self, agent):
        env = agent.create_message_envelope({"foo": "bar"}, "next_agent")
        for key in ("message_id", "timestamp", "source_agent", "target_agent", "message_type", "data"):
            assert key in env

    def test_source_agent_is_agent_name(self, agent):
        env = agent.create_message_envelope({}, "dest")
        assert env["source_agent"] == "test_agent"

    def test_target_agent_set(self, agent):
        env = agent.create_message_envelope({}, "fraud_detector")
        assert env["target_agent"] == "fraud_detector"

    def test_default_message_type(self, agent):
        env = agent.create_message_envelope({}, "dest")
        assert env["message_type"] == "transaction"

    def test_custom_message_type(self, agent):
        env = agent.create_message_envelope({}, "dest", message_type="rejection")
        assert env["message_type"] == "rejection"

    def test_data_passed_through(self, agent):
        data = {"transaction_id": "TXN001"}
        env = agent.create_message_envelope(data, "dest")
        assert env["data"] == data

    def test_message_id_is_uuid_string(self, agent):
        import uuid
        env = agent.create_message_envelope({}, "dest")
        uuid.UUID(env["message_id"])  # raises if not valid UUID


class TestReadWriteMessage:
    def test_write_then_read(self, agent, tmp_path):
        message = agent.create_message_envelope(
            {"transaction_id": "TXN001"}, "dest"
        )
        filepath = agent.write_message(message, str(tmp_path))
        loaded = agent.read_message(filepath)
        assert loaded["data"]["transaction_id"] == "TXN001"

    def test_write_creates_directory(self, agent, tmp_path):
        new_dir = tmp_path / "nested" / "dir"
        agent.write_message({"data": {"transaction_id": "X"}}, str(new_dir))
        assert new_dir.exists()

    def test_write_returns_filepath_string(self, agent, tmp_path):
        result = agent.write_message({"data": {"transaction_id": "T1"}}, str(tmp_path))
        assert isinstance(result, str)
        assert Path(result).exists()

    def test_write_filename_contains_transaction_id(self, agent, tmp_path):
        agent.write_message({"data": {"transaction_id": "TXN999"}}, str(tmp_path))
        files = list(tmp_path.glob("TXN999.json"))
        assert len(files) == 1

    def test_read_missing_file_raises(self, agent, tmp_path):
        with pytest.raises(FileNotFoundError):
            agent.read_message(str(tmp_path / "missing.json"))