"""
Tests for JSON import functionality.

Covers both array and object formats, partial failures,
malformed JSON, and the API endpoint.
"""

import io
import json
import os

from app.services.import_service import import_tickets

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestJsonImport:
    """Tests for JSON parsing and import."""

    def test_import_valid_json_array(self):
        """Direct JSON array of tickets should import successfully."""
        tickets = [
            {
                "customer_id": "C1",
                "customer_email": "a@b.com",
                "customer_name": "Alice",
                "subject": "Test issue",
                "description": "A valid description for this test ticket",
                "category": "technical_issue",
                "priority": "medium",
            }
        ]
        content = json.dumps(tickets).encode("utf-8")

        result = import_tickets(content, "json")

        assert result["total"] == 1
        assert result["successful"] == 1

    def test_import_valid_json_object(self):
        """JSON object with 'tickets' key should import successfully."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.json"), "rb") as f:
            content = f.read()

        result = import_tickets(content, "json")

        assert result["total"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0

    def test_import_json_partial_failure(self):
        """JSON with mixed valid/invalid records reports partial failure."""
        with open(os.path.join(FIXTURES_DIR, "invalid_tickets.json"), "rb") as f:
            content = f.read()

        result = import_tickets(content, "json")

        assert result["total"] == 2
        assert result["successful"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1

    def test_import_json_invalid_format(self):
        """Malformed JSON should return a parse error."""
        content = b"this is not valid json"

        result = import_tickets(content, "json")

        assert result["total"] == 0
        assert result["failed"] == 0
        assert len(result["errors"]) == 1
        assert "parse" in result["errors"][0]["errors"][0].lower() or "Failed" in result["errors"][0]["errors"][0]

    def test_import_json_via_api(self, client):
        """POST /tickets/import with a JSON file should work."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.json"), "rb") as f:
            content = f.read()

        resp = client.post(
            "/tickets/import?format=json",
            data={"file": (io.BytesIO(content), "tickets.json")},
            content_type="multipart/form-data",
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["successful"] == 2
