"""
Integration tests for end-to-end workflows.

Tests multi-step scenarios spanning API endpoints, import,
classification, and ticket lifecycle.
"""

import io
import os

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestIntegrationWorkflows:
    """End-to-end workflow tests."""

    def test_create_and_retrieve_ticket(self, client, sample_ticket_data):
        """Create a ticket, then retrieve it by ID and verify fields match."""
        # Create
        create_resp = client.post("/tickets", json=sample_ticket_data)
        assert create_resp.status_code == 201
        ticket_id = create_resp.get_json()["id"]

        # Retrieve
        get_resp = client.get(f"/tickets/{ticket_id}")
        assert get_resp.status_code == 200
        ticket = get_resp.get_json()

        assert ticket["customer_id"] == sample_ticket_data["customer_id"]
        assert ticket["subject"] == sample_ticket_data["subject"]

    def test_import_and_classify(self, client):
        """Import tickets from CSV, then auto-classify one of them."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.csv"), "rb") as f:
            csv_content = f.read()

        # Import
        import_resp = client.post(
            "/tickets/import?format=csv",
            data={"file": (io.BytesIO(csv_content), "tickets.csv")},
            content_type="multipart/form-data",
        )
        assert import_resp.status_code == 200

        # Get the first ticket
        list_resp = client.get("/tickets")
        tickets = list_resp.get_json()["tickets"]
        ticket_id = tickets[0]["id"]

        # Auto-classify
        classify_resp = client.post(f"/tickets/{ticket_id}/auto-classify")
        assert classify_resp.status_code == 200
        result = classify_resp.get_json()
        assert "classification" in result
        assert result["classification"]["confidence"] > 0

    def test_update_and_manual_override(self, client, sample_ticket_data):
        """Create, auto-classify, then manually override category -> manual_override=True."""
        # Create with auto-classify
        create_resp = client.post(
            "/tickets?auto_classify=true",
            json=sample_ticket_data,
        )
        ticket = create_resp.get_json()
        ticket_id = ticket["id"]
        assert ticket["manual_override"] is False

        # Manual override of category
        update_resp = client.put(
            f"/tickets/{ticket_id}",
            json={"category": "billing_question"},
        )
        updated = update_resp.get_json()
        assert updated["manual_override"] is True
        assert updated["category"] == "billing_question"

    def test_full_ticket_lifecycle(self, client, sample_ticket_data):
        """Create -> assign -> in_progress -> resolved; verify resolved_at is set."""
        # Create
        ticket = client.post("/tickets", json=sample_ticket_data).get_json()
        ticket_id = ticket["id"]
        assert ticket["status"] == "new"

        # Assign and move to in_progress
        client.put(f"/tickets/{ticket_id}", json={
            "status": "in_progress",
            "assigned_to": "agent@support.com",
        })

        # Resolve
        resolve_resp = client.put(f"/tickets/{ticket_id}", json={"status": "resolved"})
        resolved = resolve_resp.get_json()

        assert resolved["status"] == "resolved"
        assert resolved["resolved_at"] is not None

    def test_filter_after_bulk_import(self, client):
        """Import multiple tickets, then filter by category and priority."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.csv"), "rb") as f:
            csv_content = f.read()

        client.post(
            "/tickets/import?format=csv",
            data={"file": (io.BytesIO(csv_content), "tickets.csv")},
            content_type="multipart/form-data",
        )

        # Filter by category
        resp = client.get("/tickets?category=account_access")
        body = resp.get_json()
        assert body["count"] >= 1
        assert all(t["category"] == "account_access" for t in body["tickets"])

        # Filter by priority
        resp2 = client.get("/tickets?priority=urgent")
        body2 = resp2.get_json()
        assert all(t["priority"] == "urgent" for t in body2["tickets"])
