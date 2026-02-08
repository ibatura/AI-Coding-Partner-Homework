"""
Performance / benchmark tests.

Measures response times for critical operations to ensure
the system meets basic performance expectations.
"""

import json
import time


def _make_ticket_data(index):
    """Generate a unique valid ticket dict for bulk operations."""
    return {
        "customer_id": f"CUST-{index:04d}",
        "customer_email": f"user{index}@example.com",
        "customer_name": f"User {index}",
        "subject": f"Test ticket number {index}",
        "description": f"This is the description for test ticket number {index} with enough length",
        "category": "technical_issue",
        "priority": "medium",
    }


class TestPerformance:
    """Benchmark tests for system performance."""

    def test_create_ticket_response_time(self, client):
        """Single ticket creation should complete in under 50ms."""
        data = _make_ticket_data(1)

        start = time.perf_counter()
        resp = client.post("/tickets", json=data)
        elapsed = time.perf_counter() - start

        assert resp.status_code == 201
        assert elapsed < 0.05, f"Create ticket took {elapsed:.3f}s (limit: 0.05s)"

    def test_bulk_import_100_tickets(self, client):
        """Importing 100 tickets via JSON should complete within 2 seconds."""
        tickets = [_make_ticket_data(i) for i in range(100)]
        content = json.dumps(tickets).encode("utf-8")

        start = time.perf_counter()
        resp = client.post(
            "/tickets/import",
            data=content,
            content_type="application/json",
        )
        elapsed = time.perf_counter() - start

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["successful"] == 100
        assert elapsed < 2.0, f"Bulk import took {elapsed:.3f}s (limit: 2.0s)"

    def test_classification_throughput(self, client):
        """Classifying 100 tickets should complete within 2 seconds."""
        # Create 100 tickets first
        tickets = [_make_ticket_data(i) for i in range(100)]
        content = json.dumps(tickets).encode("utf-8")
        client.post("/tickets/import", data=content, content_type="application/json")

        # Get all ticket IDs
        list_resp = client.get("/tickets")
        ticket_ids = [t["id"] for t in list_resp.get_json()["tickets"]]

        start = time.perf_counter()
        for tid in ticket_ids:
            resp = client.post(f"/tickets/{tid}/auto-classify")
            assert resp.status_code == 200
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"100 classifications took {elapsed:.3f}s (limit: 2.0s)"

    def test_list_tickets_with_many_records(self, client):
        """GET /tickets with 500 records should respond within 500ms."""
        # Bulk create 500 tickets
        tickets = [_make_ticket_data(i) for i in range(500)]
        content = json.dumps(tickets).encode("utf-8")
        client.post("/tickets/import", data=content, content_type="application/json")

        start = time.perf_counter()
        resp = client.get("/tickets")
        elapsed = time.perf_counter() - start

        assert resp.status_code == 200
        assert resp.get_json()["count"] == 500
        assert elapsed < 0.5, f"List 500 tickets took {elapsed:.3f}s (limit: 0.5s)"

    def test_concurrent_operations(self, client):
        """Sequential create, read, update, delete cycle should complete within 200ms."""
        data = _make_ticket_data(1)

        start = time.perf_counter()

        # Create
        create_resp = client.post("/tickets", json=data)
        ticket_id = create_resp.get_json()["id"]

        # Read
        client.get(f"/tickets/{ticket_id}")

        # Update
        client.put(f"/tickets/{ticket_id}", json={"status": "in_progress"})

        # Classify
        client.post(f"/tickets/{ticket_id}/auto-classify")

        # Delete
        client.delete(f"/tickets/{ticket_id}")

        elapsed = time.perf_counter() - start

        assert elapsed < 0.2, f"CRUD cycle took {elapsed:.3f}s (limit: 0.2s)"
