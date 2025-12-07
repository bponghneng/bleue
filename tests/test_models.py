"""Tests for data models."""

import pytest

from bleue.core.models import CapeComment, CapeIssue


def test_cape_issue_creation():
    """Test basic CapeIssue creation."""
    issue = CapeIssue(id=1, description="Test issue")
    assert issue.id == 1
    assert issue.description == "Test issue"
    assert issue.status == "pending"


def test_cape_issue_trim_description():
    """Test description whitespace trimming."""
    issue = CapeIssue(id=1, description="  Test issue  ")
    assert issue.description == "Test issue"


def test_cape_issue_empty_description_validation():
    """Test that empty description raises validation error."""
    with pytest.raises(ValueError):
        CapeIssue(id=1, description="")


def test_cape_issue_default_status():
    """Test default status is set to pending."""
    issue = CapeIssue(id=1, description="Test")
    assert issue.status == "pending"


def test_cape_issue_from_supabase():
    """Test creating CapeIssue from Supabase row."""
    row = {
        "id": 1,
        "description": "Test issue",
        "status": "pending",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }
    issue = CapeIssue.from_supabase(row)
    assert issue.id == 1
    assert issue.description == "Test issue"


def test_cape_comment_creation():
    """Test basic CapeComment creation."""
    comment = CapeComment(issue_id=1, comment="Test comment")
    assert comment.issue_id == 1
    assert comment.comment == "Test comment"
    assert comment.id is None


def test_cape_comment_trim():
    """Test comment whitespace trimming."""
    comment = CapeComment(issue_id=1, comment="  Test comment  ")
    assert comment.comment == "Test comment"


def test_cape_comment_empty_validation():
    """Test that empty comment raises validation error."""
    with pytest.raises(ValueError):
        CapeComment(issue_id=1, comment="")
