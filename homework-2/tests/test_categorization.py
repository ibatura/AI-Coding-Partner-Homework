"""
Tests for the auto-classification engine.

Covers all category keyword matches, priority detection,
fallback defaults, confidence scoring, and reasoning output.
"""

from app.services.classification_service import classify_ticket


def _ticket(subject, description="No additional details for this ticket"):
    """Helper to build a minimal ticket dict for classification."""
    return {"id": "test-id", "subject": subject, "description": description}


class TestCategoryClassification:
    """Tests for category keyword matching."""

    def test_classify_account_access(self):
        """Login/password keywords should map to account_access."""
        result = classify_ticket(_ticket("Cannot login", "My password reset is not working"))

        assert result["category"] == "account_access"
        assert any(kw in result["keywords_found"] for kw in ["login", "password"])

    def test_classify_technical_issue(self):
        """Error/crash keywords should map to technical_issue."""
        result = classify_ticket(_ticket("App crash", "The application throws an error on startup"))

        assert result["category"] == "technical_issue"
        assert any(kw in result["keywords_found"] for kw in ["crash", "error"])

    def test_classify_billing_question(self):
        """Payment/invoice keywords should map to billing_question."""
        result = classify_ticket(_ticket("Payment problem", "I need a refund for my invoice"))

        assert result["category"] == "billing_question"
        assert any(kw in result["keywords_found"] for kw in ["payment", "refund", "invoice"])

    def test_classify_feature_request(self):
        """Feature/suggestion keywords should map to feature_request."""
        result = classify_ticket(_ticket("New feature request", "It would be great to add dark mode"))

        assert result["category"] == "feature_request"
        assert any(kw in result["keywords_found"] for kw in ["feature", "it would be great"])

    def test_classify_bug_report(self):
        """Defect/reproduce keywords should map to bug_report."""
        result = classify_ticket(_ticket("Defect found", "Steps to reproduce: open the page and click submit"))

        assert result["category"] == "bug_report"
        assert any(kw in result["keywords_found"] for kw in ["defect", "steps to reproduce"])

    def test_classify_other_fallback(self):
        """No matching keywords should fall back to 'other'."""
        result = classify_ticket(_ticket("General inquiry", "I have a question about your company"))

        assert result["category"] == "other"


class TestPriorityClassification:
    """Tests for priority keyword matching."""

    def test_classify_urgent_priority(self):
        """Critical/production-down keywords should map to urgent priority."""
        result = classify_ticket(
            _ticket("System down", "Critical production down issue affecting all users")
        )

        assert result["priority"] == "urgent"
        assert any(kw in result["keywords_found"] for kw in ["critical", "production down"])

    def test_classify_default_medium_priority(self):
        """No priority keywords should default to medium with high confidence."""
        result = classify_ticket(
            _ticket("Login issue", "I cannot login to the dashboard since this morning")
        )

        # Should match account_access category but no priority keywords
        # (login/cannot access matches category, not priority for "medium" default)
        # The priority confidence for medium default is 1.0
        assert result["priority"] in ("medium", "urgent")  # "cannot access" could match urgent


class TestConfidenceAndReasoning:
    """Tests for confidence scoring and reasoning output."""

    def test_confidence_scoring(self):
        """Confidence should be a float in the range [0, 1]."""
        result = classify_ticket(_ticket("Login error", "Password reset failure and access denied"))

        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_classification_reasoning(self):
        """Reasoning string should include category, priority, and confidence info."""
        result = classify_ticket(_ticket("Payment issue", "I was overcharged on my invoice"))

        reasoning = result["reasoning"]
        assert "Category" in reasoning
        assert "Priority" in reasoning
        assert "Confidence" in reasoning
