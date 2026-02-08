"""
Shared pytest fixtures for the support ticket test suite.

Provides a Flask test client, sample ticket data, and automatic
store cleanup between tests.
"""

import os
import pytest

# Point classification logs to a temp directory so tests don't pollute the project
os.environ.setdefault("CLASSIFY_LOG_DIR", "/tmp/test_classify_logs")

from app import create_app
from app.services import ticket_service


@pytest.fixture()
def app():
    """Create a Flask application configured for testing."""
    application = create_app("development")
    application.config["TESTING"] = True
    yield application


@pytest.fixture()
def client(app):
    """Flask test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_store():
    """Clear the in-memory ticket store before each test."""
    ticket_service.reset_store()
    yield
    ticket_service.reset_store()


@pytest.fixture()
def sample_ticket_data():
    """Return a valid ticket data dict suitable for creation."""
    return {
        "customer_id": "CUST-001",
        "customer_email": "john@example.com",
        "customer_name": "John Doe",
        "subject": "Cannot login to my account",
        "description": "I have been unable to login since yesterday morning. Password reset does not work.",
        "category": "account_access",
        "priority": "high",
        "tags": ["login", "urgent"],
        "metadata": {
            "source": "web_form",
            "device_type": "desktop",
        },
    }


@pytest.fixture()
def created_ticket(client, sample_ticket_data):
    """Create and return a ticket via the API for tests that need a pre-existing ticket."""
    resp = client.post("/tickets", json=sample_ticket_data)
    return resp.get_json()
