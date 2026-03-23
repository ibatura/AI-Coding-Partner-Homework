"""Shared pytest fixtures for the banking pipeline test suite."""

import json
import pytest


VALID_TXN = {
    "transaction_id": "TXN001",
    "timestamp": "2026-03-16T09:00:00Z",
    "source_account": "ACC-1001",
    "destination_account": "ACC-2001",
    "amount": "1500.00",
    "currency": "USD",
    "transaction_type": "transfer",
    "description": "Monthly rent payment",
    "metadata": {"channel": "online", "country": "US"},
}

HIGH_VALUE_TXN = {
    "transaction_id": "TXN005",
    "timestamp": "2026-03-16T10:00:00Z",
    "source_account": "ACC-1005",
    "destination_account": "ACC-6600",
    "amount": "75000.00",
    "currency": "USD",
    "transaction_type": "wire_transfer",
    "description": "Property settlement",
    "metadata": {"channel": "branch", "country": "US"},
}

CROSS_BORDER_NIGHT_TXN = {
    "transaction_id": "TXN004",
    "timestamp": "2026-03-16T02:47:00Z",
    "source_account": "ACC-1004",
    "destination_account": "ACC-5500",
    "amount": "500.00",
    "currency": "EUR",
    "transaction_type": "transfer",
    "description": "Invoice #4471",
    "metadata": {"channel": "api", "country": "DE"},
}


@pytest.fixture
def valid_txn():
    return dict(VALID_TXN)


@pytest.fixture
def high_value_txn():
    return dict(HIGH_VALUE_TXN)


@pytest.fixture
def cross_border_night_txn():
    return dict(CROSS_BORDER_NIGHT_TXN)


@pytest.fixture
def valid_message(valid_txn):
    return {
        "message_id": "test-msg-id",
        "timestamp": "2026-03-16T09:00:00Z",
        "source_agent": "integrator",
        "target_agent": "transaction_validator",
        "message_type": "transaction",
        "data": valid_txn,
    }


@pytest.fixture
def shared_dirs(tmp_path):
    """Create the shared/ directory tree under tmp_path and return the root."""
    for sub in ("input", "processing", "output", "results"):
        (tmp_path / "shared" / sub).mkdir(parents=True)
    return tmp_path


@pytest.fixture
def sample_transactions_file(tmp_path):
    """Write a minimal sample-transactions.json to tmp_path."""
    transactions = [
        {
            "transaction_id": "TXN001",
            "timestamp": "2026-03-16T09:00:00Z",
            "source_account": "ACC-1001",
            "destination_account": "ACC-2001",
            "amount": "1500.00",
            "currency": "USD",
            "transaction_type": "transfer",
            "description": "Rent",
            "metadata": {"channel": "online", "country": "US"},
        },
        {
            "transaction_id": "TXN006",
            "timestamp": "2026-03-16T10:05:00Z",
            "source_account": "ACC-1006",
            "destination_account": "ACC-7700",
            "amount": "200.00",
            "currency": "XYZ",
            "transaction_type": "transfer",
            "description": "Test",
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
    ]
    path = tmp_path / "sample-transactions.json"
    path.write_text(json.dumps(transactions))
    return str(path)