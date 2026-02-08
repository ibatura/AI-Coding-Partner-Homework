"""
Tests for the ticket REST API endpoints.

Covers all CRUD operations, auto-classification via API,
filtering, and error responses.
"""

import json


class TestCreateTicket:
    """POST /tickets endpoint tests."""

    def test_create_ticket_success(self, client, sample_ticket_data):
        """POST /tickets with valid data returns 201 and the ticket."""
        resp = client.post("/tickets", json=sample_ticket_data)

        assert resp.status_code == 201
        data = resp.get_json()
        assert data["customer_id"] == "CUST-001"
        assert data["status"] == "new"
        assert "id" in data

    def test_create_ticket_validation_error(self, client):
        """POST /tickets with missing fields returns 400."""
        resp = client.post("/tickets", json={"customer_id": "C1"})

        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"] == "Validation failed"
        assert len(data["details"]) > 0

    def test_create_ticket_with_auto_classify(self, client, sample_ticket_data):
        """POST /tickets?auto_classify=true runs classification on the ticket."""
        resp = client.post(
            "/tickets?auto_classify=true",
            json=sample_ticket_data,
        )

        assert resp.status_code == 201
        data = resp.get_json()
        # Classification should have populated these fields
        assert data["classification_confidence"] is not None
        assert data["classified_at"] is not None


class TestListTickets:
    """GET /tickets endpoint tests."""

    def test_list_tickets(self, client, sample_ticket_data):
        """GET /tickets returns all created tickets."""
        # Create two tickets
        client.post("/tickets", json=sample_ticket_data)
        data2 = sample_ticket_data.copy()
        data2["customer_id"] = "CUST-002"
        data2["customer_email"] = "jane@example.com"
        client.post("/tickets", json=data2)

        resp = client.get("/tickets")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["count"] == 2

    def test_list_tickets_with_filters(self, client, sample_ticket_data):
        """GET /tickets?priority=high returns only matching tickets."""
        # Create a high-priority ticket
        client.post("/tickets", json=sample_ticket_data)

        # Create a low-priority ticket
        low = sample_ticket_data.copy()
        low["customer_id"] = "CUST-002"
        low["customer_email"] = "other@example.com"
        low["priority"] = "low"
        client.post("/tickets", json=low)

        resp = client.get("/tickets?priority=high")
        body = resp.get_json()
        assert body["count"] == 1
        assert body["tickets"][0]["priority"] == "high"


class TestGetTicket:
    """GET /tickets/<id> endpoint tests."""

    def test_get_ticket_success(self, client, created_ticket):
        """GET /tickets/<id> returns the ticket."""
        ticket_id = created_ticket["id"]
        resp = client.get(f"/tickets/{ticket_id}")

        assert resp.status_code == 200
        assert resp.get_json()["id"] == ticket_id

    def test_get_ticket_not_found(self, client):
        """GET /tickets/<id> with nonexistent ID returns 404."""
        resp = client.get("/tickets/nonexistent-id")
        assert resp.status_code == 404
        assert resp.get_json()["error"] == "Ticket not found"


class TestUpdateTicket:
    """PUT /tickets/<id> endpoint tests."""

    def test_update_ticket_success(self, client, created_ticket):
        """PUT /tickets/<id> with valid data returns 200."""
        ticket_id = created_ticket["id"]
        resp = client.put(
            f"/tickets/{ticket_id}",
            json={"status": "in_progress", "assigned_to": "agent@support.com"},
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "in_progress"
        assert data["assigned_to"] == "agent@support.com"

    def test_update_ticket_not_found(self, client):
        """PUT /tickets/<id> with nonexistent ID returns 404."""
        resp = client.put("/tickets/nonexistent-id", json={"status": "closed"})
        assert resp.status_code == 404


class TestDeleteTicket:
    """DELETE /tickets/<id> endpoint tests."""

    def test_delete_ticket_success(self, client, created_ticket):
        """DELETE /tickets/<id> removes the ticket and returns 200."""
        ticket_id = created_ticket["id"]
        resp = client.delete(f"/tickets/{ticket_id}")

        assert resp.status_code == 200
        assert "deleted" in resp.get_json()["message"].lower()

        # Verify it's gone
        get_resp = client.get(f"/tickets/{ticket_id}")
        assert get_resp.status_code == 404

    def test_delete_ticket_not_found(self, client):
        """DELETE /tickets/<id> with nonexistent ID returns 404."""
        resp = client.delete("/tickets/nonexistent-id")
        assert resp.status_code == 404
