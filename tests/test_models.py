"""Tests for data models."""

import pytest

from bleue.core.models import BleueComment, BleueIssue


def test_bleue_issue_creation():
    """Test basic BleueIssue creation."""
    issue = BleueIssue(id=1, description="Test issue")
    assert issue.id == 1
    assert issue.description == "Test issue"
    assert issue.status == "pending"


def test_bleue_issue_trim_description():
    """Test description whitespace trimming."""
    issue = BleueIssue(id=1, description="  Test issue  ")
    assert issue.description == "Test issue"


def test_bleue_issue_empty_description_validation():
    """Test that empty description raises validation error."""
    with pytest.raises(ValueError):
        BleueIssue(id=1, description="")


def test_bleue_issue_default_status():
    """Test default status is set to pending."""
    issue = BleueIssue(id=1, description="Test")
    assert issue.status == "pending"


def test_bleue_issue_from_supabase():
    """Test creating BleueIssue from Supabase row."""
    row = {
        "id": 1,
        "description": "Test issue",
        "status": "pending",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }
    issue = BleueIssue.from_supabase(row)
    assert issue.id == 1
    assert issue.description == "Test issue"


def test_bleue_comment_creation():
    """Test basic BleueComment creation."""
    comment = BleueComment(issue_id=1, comment="Test comment")
    assert comment.issue_id == 1
    assert comment.comment == "Test comment"
    assert comment.id is None


def test_bleue_comment_trim():
    """Test comment whitespace trimming."""
    comment = BleueComment(issue_id=1, comment="  Test comment  ")
    assert comment.comment == "Test comment"


def test_bleue_comment_empty_validation():
    """Test that empty comment raises validation error."""
    with pytest.raises(ValueError):
        BleueComment(issue_id=1, comment="")
