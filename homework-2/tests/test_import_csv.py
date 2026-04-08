"""
Tests for CSV import functionality.

Covers valid imports, tag parsing, metadata dot-notation,
partial failures, empty files, and the API endpoint.
"""

import io
import os

from app.services.import_service import import_tickets

# Path to fixture files
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestCsvImport:
    """Tests for CSV parsing and import."""

    def test_import_valid_csv(self):
        """Valid CSV with 3 rows should import all successfully."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.csv"), "rb") as f:
            content = f.read()

        result = import_tickets(content, "csv")

        assert result["total"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0
        assert result["errors"] == []

    def test_import_csv_with_tags(self):
        """Semicolon-separated tags field should be parsed into a list."""
        csv_content = (
            "customer_id,customer_email,customer_name,subject,description,category,priority,tags\n"
            "C1,a@b.com,Alice,Issue,A test ticket description here,bug_report,low,tag1;tag2;tag3\n"
        ).encode("utf-8")

        result = import_tickets(csv_content, "csv")

        assert result["successful"] == 1
        # Verify tags were parsed (ticket is stored in-memory)
        from app.services.ticket_service import get_all_tickets
        tickets = get_all_tickets()
        assert tickets[0]["tags"] == ["tag1", "tag2", "tag3"]

    def test_import_csv_with_metadata(self):
        """Dot-notation metadata fields (metadata.source) should be grouped."""
        csv_content = (
            "customer_id,customer_email,customer_name,subject,description,category,priority,metadata.source,metadata.device_type\n"
            "C1,a@b.com,Alice,Issue,A test ticket description here,bug_report,low,web_form,desktop\n"
        ).encode("utf-8")

        result = import_tickets(csv_content, "csv")

        assert result["successful"] == 1
        from app.services.ticket_service import get_all_tickets
        tickets = get_all_tickets()
        assert tickets[0]["metadata"]["source"] == "web_form"
        assert tickets[0]["metadata"]["device_type"] == "desktop"

    def test_import_csv_partial_failure(self):
        """CSV with mix of valid and invalid rows should report partial failure."""
        with open(os.path.join(FIXTURES_DIR, "invalid_tickets.csv"), "rb") as f:
            content = f.read()

        result = import_tickets(content, "csv")

        assert result["total"] == 3
        assert result["successful"] == 2
        assert result["failed"] == 1
        assert len(result["errors"]) == 1
        # Row 2 is the invalid one (1-indexed)
        assert result["errors"][0]["row"] == 2

    def test_import_csv_empty_file(self):
        """Empty CSV (headers only) should return zero total."""
        csv_content = b"customer_id,customer_email,customer_name,subject,description,category,priority\n"
        result = import_tickets(csv_content, "csv")

        assert result["total"] == 0
        assert result["successful"] == 0

    def test_import_csv_via_api(self, client):
        """POST /tickets/import with a CSV file upload should work."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.csv"), "rb") as f:
            content = f.read()

        resp = client.post(
            "/tickets/import?format=csv",
            data={"file": (io.BytesIO(content), "tickets.csv")},
            content_type="multipart/form-data",
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["successful"] == 3
