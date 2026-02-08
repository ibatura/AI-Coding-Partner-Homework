"""
Tests for XML import functionality.

Covers multi-ticket import, single-ticket root, tag elements,
partial failures, and the API endpoint.
"""

import io
import os

from app.services.import_service import import_tickets

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestXmlImport:
    """Tests for XML parsing and import."""

    def test_import_valid_xml(self):
        """Multiple <ticket> elements under <tickets> root should import."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.xml"), "rb") as f:
            content = f.read()

        result = import_tickets(content, "xml")

        assert result["total"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0

    def test_import_single_ticket_xml(self):
        """A single <ticket> as root element should be accepted."""
        xml_content = b"""<?xml version="1.0"?>
        <ticket>
            <customer_id>C1</customer_id>
            <customer_email>a@b.com</customer_email>
            <customer_name>Alice</customer_name>
            <subject>Test issue</subject>
            <description>A valid description for this test ticket</description>
            <category>technical_issue</category>
            <priority>medium</priority>
        </ticket>
        """

        result = import_tickets(xml_content, "xml")

        assert result["total"] == 1
        assert result["successful"] == 1

    def test_import_xml_with_tags(self):
        """<tags><tag> elements should be parsed into a list."""
        xml_content = b"""<?xml version="1.0"?>
        <tickets>
            <ticket>
                <customer_id>C1</customer_id>
                <customer_email>a@b.com</customer_email>
                <customer_name>Alice</customer_name>
                <subject>Test issue</subject>
                <description>A valid description for this test ticket</description>
                <category>technical_issue</category>
                <priority>medium</priority>
                <tags>
                    <tag>bug</tag>
                    <tag>critical</tag>
                </tags>
            </ticket>
        </tickets>
        """

        result = import_tickets(xml_content, "xml")
        assert result["successful"] == 1

        from app.services.ticket_service import get_all_tickets
        tickets = get_all_tickets()
        assert tickets[0]["tags"] == ["bug", "critical"]

    def test_import_xml_partial_failure(self):
        """XML with mixed valid/invalid records reports partial failure."""
        with open(os.path.join(FIXTURES_DIR, "invalid_tickets.xml"), "rb") as f:
            content = f.read()

        result = import_tickets(content, "xml")

        assert result["total"] == 2
        assert result["successful"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1

    def test_import_xml_via_api(self, client):
        """POST /tickets/import with an XML file should work."""
        with open(os.path.join(FIXTURES_DIR, "valid_tickets.xml"), "rb") as f:
            content = f.read()

        resp = client.post(
            "/tickets/import?format=xml",
            data={"file": (io.BytesIO(content), "tickets.xml")},
            content_type="multipart/form-data",
        )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["successful"] == 2
