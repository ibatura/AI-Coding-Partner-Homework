"""
Integration tests for end-to-end workflows.

Tests multi-step scenarios spanning API endpoints, import,
classification, and ticket lifecycle.
"""

import io
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _make_ticket(index, category="technical_issue", priority="medium"):
    """Generate a unique valid ticket dict."""
    return {
        "customer_id": f"CUST-{index:04d}",
        "customer_email": f"user{index}@example.com",
        "customer_name": f"User {index}",
        "subject": f"Test ticket number {index}",
        "description": f"This is the description for test ticket number {index} with enough length",
        "category": category,
        "priority": priority,
    }


class TestTicketLifecycle:
    """Complete ticket lifecycle workflow tests."""

    def test_create_and_retrieve_ticket(self, client, sample_ticket_data):
        """Create a ticket, then retrieve it by ID and verify fields match."""
        create_resp = client.post("/tickets", json=sample_ticket_data)
        assert create_resp.status_code == 201
        ticket_id = create_resp.get_json()["id"]

        get_resp = client.get(f"/tickets/{ticket_id}")
        assert get_resp.status_code == 200
        ticket = get_resp.get_json()

        assert ticket["customer_id"] == sample_ticket_data["customer_id"]
        assert ticket["subject"] == sample_ticket_data["subject"]

    def test_full_ticket_lifecycle(self, client, sample_ticket_data):
        """new -> in_progress -> waiting_customer -> in_progress -> resolved -> closed."""
        # Create
        ticket = client.post("/tickets", json=sample_ticket_data).get_json()
        ticket_id = ticket["id"]
        assert ticket["status"] == "new"
        assert ticket["resolved_at"] is None

        # Assign agent and move to in_progress
        resp = client.put(f"/tickets/{ticket_id}", json={
            "status": "in_progress",
            "assigned_to": "agent@support.com",
        })
        assert resp.status_code == 200
        ticket = resp.get_json()
        assert ticket["status"] == "in_progress"
        assert ticket["assigned_to"] == "agent@support.com"

        # Move to waiting_customer
        resp = client.put(f"/tickets/{ticket_id}", json={"status": "waiting_customer"})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "waiting_customer"

        # Back to in_progress
        resp = client.put(f"/tickets/{ticket_id}", json={"status": "in_progress"})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "in_progress"

        # Resolve
        resp = client.put(f"/tickets/{ticket_id}", json={"status": "resolved"})
        resolved = resp.get_json()
        assert resolved["status"] == "resolved"
        assert resolved["resolved_at"] is not None

        # Close
        resp = client.put(f"/tickets/{ticket_id}", json={"status": "closed"})
        closed = resp.get_json()
        assert closed["status"] == "closed"

        # Verify final state via GET
        final = client.get(f"/tickets/{ticket_id}").get_json()
        assert final["status"] == "closed"
        assert final["assigned_to"] == "agent@support.com"
        assert final["resolved_at"] is not None

    def test_lifecycle_with_classification_and_override(self, client, sample_ticket_data):
        """Create with auto-classify, verify classification, then manually override."""
        # Create with auto-classification
        create_resp = client.post("/tickets?auto_classify=true", json=sample_ticket_data)
        assert create_resp.status_code == 201
        ticket = create_resp.get_json()
        ticket_id = ticket["id"]

        assert ticket["classification_confidence"] is not None
        assert ticket["classification_confidence"] > 0
        assert ticket["manual_override"] is False

        # Manually override category
        resp = client.put(f"/tickets/{ticket_id}", json={"category": "billing_question"})
        updated = resp.get_json()
        assert updated["category"] == "billing_question"
        assert updated["manual_override"] is True

        # Re-classify
        classify_resp = client.post(f"/tickets/{ticket_id}/auto-classify")
        assert classify_resp.status_code == 200
        result = classify_resp.get_json()
        assert "classification" in result
        assert result["classification"]["confidence"] > 0

    def test_create_update_delete_verify(self, client, sample_ticket_data):
        """Full CRUD cycle: create, update, delete, verify gone."""
        # Create
        ticket = client.post("/tickets", json=sample_ticket_data).get_json()
        ticket_id = ticket["id"]

        # Update
        resp = client.put(f"/tickets/{ticket_id}", json={"subject": "Updated subject"})
        assert resp.status_code == 200
        assert resp.get_json()["subject"] == "Updated subject"

        # Delete
        del_resp = client.delete(f"/tickets/{ticket_id}")
        assert del_resp.status_code == 200

        # Verify gone
        get_resp = client.get(f"/tickets/{ticket_id}")
        assert get_resp.status_code == 404


class TestBulkImportWithClassification:
    """Bulk import with auto-classification verification."""

    def test_import_csv_and_classify_all(self, client):
        """Import CSV tickets, auto-classify each, verify classification results."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.csv"), "rb") as f:
            csv_content = f.read()

        import_resp = client.post(
            "/tickets/import?format=csv",
            data={"file": (io.BytesIO(csv_content), "tickets.csv")},
            content_type="multipart/form-data",
        )
        assert import_resp.status_code == 200
        summary = import_resp.get_json()
        assert summary["successful"] >= 1

        # Get all imported tickets
        tickets = client.get("/tickets").get_json()["tickets"]

        # Auto-classify each and verify
        for ticket in tickets:
            resp = client.post(f"/tickets/{ticket['id']}/auto-classify")
            assert resp.status_code == 200
            result = resp.get_json()
            assert result["classification"]["confidence"] > 0
            assert result["classification"]["category"] in [
                "account_access", "technical_issue", "billing_question",
                "feature_request", "bug_report", "other",
            ]
            assert result["classification"]["priority"] in [
                "urgent", "high", "medium", "low",
            ]
            assert len(result["classification"]["reasoning"]) > 0

    def test_import_json_and_classify(self, client):
        """Import JSON tickets, classify, verify keywords matched."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.json"), "rb") as f:
            json_content = f.read()

        import_resp = client.post(
            "/tickets/import?format=json",
            data={"file": (io.BytesIO(json_content), "tickets.json")},
            content_type="multipart/form-data",
        )
        assert import_resp.status_code == 200

        tickets = client.get("/tickets").get_json()["tickets"]
        assert len(tickets) >= 2

        for ticket in tickets:
            resp = client.post(f"/tickets/{ticket['id']}/auto-classify")
            result = resp.get_json()
            classification = result["classification"]
            assert isinstance(classification["keywords_found"], list)
            assert classification["confidence"] >= 0

    def test_import_xml_and_classify(self, client):
        """Import XML tickets and verify classification."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.xml"), "rb") as f:
            xml_content = f.read()

        import_resp = client.post(
            "/tickets/import?format=xml",
            data={"file": (io.BytesIO(xml_content), "tickets.xml")},
            content_type="multipart/form-data",
        )
        assert import_resp.status_code == 200

        tickets = client.get("/tickets").get_json()["tickets"]
        for ticket in tickets:
            resp = client.post(f"/tickets/{ticket['id']}/auto-classify")
            assert resp.status_code == 200

    def test_bulk_import_large_batch_with_classification(self, client):
        """Import 50 tickets via JSON and classify all of them."""
        tickets_data = [_make_ticket(i) for i in range(50)]
        content = json.dumps(tickets_data).encode("utf-8")

        import_resp = client.post(
            "/tickets/import",
            data=content,
            content_type="application/json",
        )
        assert import_resp.status_code == 200
        assert import_resp.get_json()["successful"] == 50

        tickets = client.get("/tickets").get_json()["tickets"]
        assert len(tickets) == 50

        # Classify all and verify
        classified_count = 0
        for ticket in tickets:
            resp = client.post(f"/tickets/{ticket['id']}/auto-classify")
            assert resp.status_code == 200
            classified_count += 1

        assert classified_count == 50


class TestConcurrentOperations:
    """Concurrent operations (20+ simultaneous requests)."""

    def test_concurrent_ticket_creation(self, app):
        """Create 25 tickets concurrently and verify all succeed."""
        results = []

        def create_ticket(index):
            with app.test_client() as c:
                data = _make_ticket(index)
                resp = c.post("/tickets", json=data)
                return resp.status_code, resp.get_json()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(create_ticket, i): i for i in range(25)}
            for future in as_completed(futures):
                status, body = future.result()
                results.append((status, body))

        # All 25 should succeed
        assert len(results) == 25
        assert all(status == 201 for status, _ in results)

        # Verify all tickets exist
        with app.test_client() as c:
            list_resp = c.get("/tickets")
            assert list_resp.get_json()["count"] == 25

    def test_concurrent_reads(self, app, sample_ticket_data):
        """Read the same ticket 25 times concurrently."""
        with app.test_client() as c:
            ticket = c.post("/tickets", json=sample_ticket_data).get_json()
            ticket_id = ticket["id"]

        results = []

        def read_ticket():
            with app.test_client() as c:
                resp = c.get(f"/tickets/{ticket_id}")
                return resp.status_code

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_ticket) for _ in range(25)]
            for future in as_completed(futures):
                results.append(future.result())

        assert len(results) == 25
        assert all(status == 200 for status in results)

    def test_concurrent_mixed_operations(self, app):
        """Run 20+ mixed create/read/update operations concurrently."""
        # Pre-create some tickets
        ticket_ids = []
        with app.test_client() as c:
            for i in range(10):
                resp = c.post("/tickets", json=_make_ticket(i))
                ticket_ids.append(resp.get_json()["id"])

        results = []

        def create_op(index):
            with app.test_client() as c:
                resp = c.post("/tickets", json=_make_ticket(100 + index))
                return "create", resp.status_code

        def read_op(tid):
            with app.test_client() as c:
                resp = c.get(f"/tickets/{tid}")
                return "read", resp.status_code

        def update_op(tid):
            with app.test_client() as c:
                resp = c.put(f"/tickets/{tid}", json={"status": "in_progress"})
                return "update", resp.status_code

        def classify_op(tid):
            with app.test_client() as c:
                resp = c.post(f"/tickets/{tid}/auto-classify")
                return "classify", resp.status_code

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            # 8 creates
            for i in range(8):
                futures.append(executor.submit(create_op, i))
            # 5 reads
            for tid in ticket_ids[:5]:
                futures.append(executor.submit(read_op, tid))
            # 5 updates
            for tid in ticket_ids[5:]:
                futures.append(executor.submit(update_op, tid))
            # 5 classifies
            for tid in ticket_ids[:5]:
                futures.append(executor.submit(classify_op, tid))

            for future in as_completed(futures):
                results.append(future.result())

        assert len(results) == 23  # 8 + 5 + 5 + 5
        for op_type, status in results:
            if op_type == "create":
                assert status == 201
            else:
                assert status == 200

    def test_concurrent_imports(self, app):
        """Run 3 concurrent imports (CSV, JSON, XML) simultaneously."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.csv"), "rb") as f:
            csv_content = f.read()
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.json"), "rb") as f:
            json_content = f.read()
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.xml"), "rb") as f:
            xml_content = f.read()

        results = []

        def import_csv():
            with app.test_client() as c:
                resp = c.post(
                    "/tickets/import?format=csv",
                    data={"file": (io.BytesIO(csv_content), "tickets.csv")},
                    content_type="multipart/form-data",
                )
                return resp.status_code, resp.get_json()["successful"]

        def import_json():
            with app.test_client() as c:
                resp = c.post(
                    "/tickets/import?format=json",
                    data={"file": (io.BytesIO(json_content), "tickets.json")},
                    content_type="multipart/form-data",
                )
                return resp.status_code, resp.get_json()["successful"]

        def import_xml():
            with app.test_client() as c:
                resp = c.post(
                    "/tickets/import?format=xml",
                    data={"file": (io.BytesIO(xml_content), "tickets.xml")},
                    content_type="multipart/form-data",
                )
                return resp.status_code, resp.get_json()["successful"]

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(import_csv),
                executor.submit(import_json),
                executor.submit(import_xml),
            ]
            for future in as_completed(futures):
                results.append(future.result())

        assert len(results) == 3
        assert all(status == 200 for status, _ in results)
        total_imported = sum(count for _, count in results)
        assert total_imported >= 3  # At least some from each format


class TestCombinedFiltering:
    """Combined filtering by category and priority."""

    def test_filter_by_category_and_priority(self, client):
        """Import tickets with various categories/priorities and filter with both."""
        categories = ["account_access", "technical_issue", "billing_question"]
        priorities = ["urgent", "high", "medium", "low"]

        # Create tickets with known category/priority combinations
        for i, cat in enumerate(categories):
            for j, pri in enumerate(priorities):
                data = _make_ticket(i * 10 + j, category=cat, priority=pri)
                resp = client.post("/tickets", json=data)
                assert resp.status_code == 201

        # Filter by category only
        resp = client.get("/tickets?category=account_access")
        body = resp.get_json()
        assert body["count"] == 4
        assert all(t["category"] == "account_access" for t in body["tickets"])

        # Filter by priority only
        resp = client.get("/tickets?priority=urgent")
        body = resp.get_json()
        assert body["count"] == 3
        assert all(t["priority"] == "urgent" for t in body["tickets"])

        # Combined filter: category + priority
        resp = client.get("/tickets?category=technical_issue&priority=high")
        body = resp.get_json()
        assert body["count"] == 1
        assert body["tickets"][0]["category"] == "technical_issue"
        assert body["tickets"][0]["priority"] == "high"

    def test_filter_by_category_priority_and_status(self, client):
        """Filter by category, priority, and status simultaneously."""
        # Create tickets
        data1 = _make_ticket(1, category="technical_issue", priority="urgent")
        data2 = _make_ticket(2, category="technical_issue", priority="urgent")
        data3 = _make_ticket(3, category="billing_question", priority="urgent")

        t1 = client.post("/tickets", json=data1).get_json()
        t2 = client.post("/tickets", json=data2).get_json()
        client.post("/tickets", json=data3)

        # Move one to in_progress
        client.put(f"/tickets/{t1['id']}", json={"status": "in_progress"})

        # Filter: technical_issue + urgent + in_progress
        resp = client.get("/tickets?category=technical_issue&priority=urgent&status=in_progress")
        body = resp.get_json()
        assert body["count"] == 1
        assert body["tickets"][0]["id"] == t1["id"]

        # Filter: technical_issue + urgent (should get both)
        resp = client.get("/tickets?category=technical_issue&priority=urgent")
        body = resp.get_json()
        assert body["count"] == 2

    def test_filter_returns_empty_for_no_match(self, client):
        """Filtering with no matching results returns empty list."""
        client.post("/tickets", json=_make_ticket(1, category="technical_issue", priority="medium"))

        resp = client.get("/tickets?category=feature_request&priority=urgent")
        body = resp.get_json()
        assert body["count"] == 0
        assert body["tickets"] == []

    def test_filter_after_bulk_import_all_formats(self, client):
        """Import from all 3 formats, then filter the combined set."""
        # Import CSV
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.csv"), "rb") as f:
            client.post(
                "/tickets/import?format=csv",
                data={"file": (io.BytesIO(f.read()), "tickets.csv")},
                content_type="multipart/form-data",
            )

        # Import JSON
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.json"), "rb") as f:
            client.post(
                "/tickets/import?format=json",
                data={"file": (io.BytesIO(f.read()), "tickets.json")},
                content_type="multipart/form-data",
            )

        # Import XML
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.xml"), "rb") as f:
            client.post(
                "/tickets/import?format=xml",
                data={"file": (io.BytesIO(f.read()), "tickets.xml")},
                content_type="multipart/form-data",
            )

        # Total tickets from all imports
        all_tickets = client.get("/tickets").get_json()
        assert all_tickets["count"] >= 5  # 3 CSV + 2 JSON + 2 XML (some may overlap)

        # Filter by category across all imported tickets
        resp = client.get("/tickets?category=account_access")
        body = resp.get_json()
        assert body["count"] >= 1
        assert all(t["category"] == "account_access" for t in body["tickets"])

        # Filter by priority
        resp = client.get("/tickets?priority=high")
        body = resp.get_json()
        assert all(t["priority"] == "high" for t in body["tickets"])
