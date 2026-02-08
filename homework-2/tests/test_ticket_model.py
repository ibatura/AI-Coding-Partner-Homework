"""
Tests for the Ticket model and validators.

Covers ticket creation, auto-generated fields, serialization,
partial updates, classification application, and field validation.
"""

from app.models.ticket import Ticket
from app.utils.validators import validate_ticket_data, validate_email, validate_string_length, validate_enum


# -- Sample data used across tests --

def _valid_data():
    """Return a minimal valid ticket data dict."""
    return {
        "customer_id": "CUST-001",
        "customer_email": "test@example.com",
        "customer_name": "Test User",
        "subject": "Test subject",
        "description": "This is a valid test description for the ticket",
        "category": "technical_issue",
        "priority": "medium",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestTicketModel:
    """Tests for the Ticket class."""

    def test_create_ticket_with_valid_data(self):
        """All required fields should produce a valid Ticket instance."""
        data = _valid_data()
        ticket = Ticket(data)

        assert ticket.customer_id == "CUST-001"
        assert ticket.customer_email == "test@example.com"
        assert ticket.customer_name == "Test User"
        assert ticket.subject == "Test subject"
        assert ticket.category == "technical_issue"
        assert ticket.priority == "medium"

    def test_auto_generated_fields(self):
        """id, created_at, and updated_at should be auto-generated."""
        ticket = Ticket(_valid_data())

        # UUID format check
        assert len(ticket.id) == 36
        assert "-" in ticket.id
        # Timestamps should be ISO-8601 strings
        assert "T" in ticket.created_at
        assert "T" in ticket.updated_at

    def test_default_field_values(self):
        """status defaults to 'new', tags to [], metadata to {}."""
        ticket = Ticket(_valid_data())

        assert ticket.status == "new"
        assert ticket.tags == []
        assert ticket.metadata == {}
        assert ticket.resolved_at is None
        assert ticket.assigned_to is None
        assert ticket.manual_override is False

    def test_ticket_to_dict(self):
        """to_dict() should return all expected fields."""
        ticket = Ticket(_valid_data())
        d = ticket.to_dict()

        expected_keys = {
            "id", "customer_id", "customer_email", "customer_name",
            "subject", "description", "category", "priority", "status",
            "created_at", "updated_at", "resolved_at", "assigned_to",
            "tags", "metadata", "classification_confidence",
            "classification_reasoning", "classification_keywords",
            "classified_at", "manual_override",
        }
        assert set(d.keys()) == expected_keys

    def test_update_ticket_fields(self):
        """Partial update should modify only specified fields."""
        ticket = Ticket(_valid_data())
        original_subject = ticket.subject

        ticket.update({"assigned_to": "agent@support.com"})

        assert ticket.assigned_to == "agent@support.com"
        assert ticket.subject == original_subject  # unchanged

    def test_update_sets_resolved_at(self):
        """Changing status to 'resolved' or 'closed' sets resolved_at."""
        ticket = Ticket(_valid_data())
        assert ticket.resolved_at is None

        ticket.update({"status": "resolved"})

        assert ticket.resolved_at is not None
        assert ticket.status == "resolved"

    def test_apply_classification(self):
        """apply_classification() should set all classification fields."""
        ticket = Ticket(_valid_data())
        result = {
            "category": "billing_question",
            "priority": "urgent",
            "confidence": 0.85,
            "reasoning": "Matched keywords: payment, invoice",
            "keywords_found": ["payment", "invoice"],
        }

        ticket.apply_classification(result)

        assert ticket.category == "billing_question"
        assert ticket.priority == "urgent"
        assert ticket.classification_confidence == 0.85
        assert ticket.classification_reasoning == "Matched keywords: payment, invoice"
        assert ticket.classification_keywords == ["payment", "invoice"]
        assert ticket.classified_at is not None
        # apply_classification does NOT set manual_override
        assert ticket.manual_override is False


class TestValidation:
    """Tests for the validators module."""

    def test_validate_required_fields_missing(self):
        """Missing required fields should produce errors on creation."""
        errors = validate_ticket_data({}, is_update=False)

        # All 7 required fields should be flagged
        assert len(errors) >= 7
        assert any("customer_id" in e for e in errors)
        assert any("customer_email" in e for e in errors)
        assert any("subject" in e for e in errors)

    def test_validate_invalid_enum_values(self):
        """Invalid enum values for category, priority, status should be rejected."""
        data = _valid_data()
        data["category"] = "nonexistent_category"
        data["priority"] = "super_high"
        data["status"] = "unknown_status"

        errors = validate_ticket_data(data, is_update=False)

        assert any("category" in e for e in errors)
        assert any("priority" in e for e in errors)
        assert any("status" in e for e in errors)
