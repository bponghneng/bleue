"""Tests for data models."""

import pytest
from pydantic import ValidationError

from bleue.core.models import BleueComment, BleueIssue


def test_bleue_issue_creation() -> None:
    """Test basic BleueIssue creation."""
    issue = BleueIssue(id=1, description="Test issue")
    assert issue.id == 1
    assert issue.description == "Test issue"
    assert issue.status == "pending"


def test_bleue_issue_trim_description() -> None:
    """Test description whitespace trimming."""
    issue = BleueIssue(id=1, description="  Test issue  ")
    assert issue.description == "Test issue"


def test_bleue_issue_empty_description_validation() -> None:
    """Test that empty description raises validation error."""
    with pytest.raises(ValidationError, match="description"):
        BleueIssue(id=1, description="")


def test_bleue_issue_default_status() -> None:
    """Test default status is set to pending."""
    issue = BleueIssue(id=1, description="Test")
    assert issue.status == "pending"


def test_bleue_issue_from_supabase() -> None:
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


def test_bleue_issue_type_default_none():
    """Test that BleueIssue type defaults to None."""
    issue = BleueIssue(id=1, description="Test issue")
    assert issue.type is None


def test_bleue_issue_type_main():
    """Test BleueIssue accepts type='main'."""
    issue = BleueIssue(id=1, description="Test issue", type="main")
    assert issue.type == "main"


def test_bleue_issue_type_patch():
    """Test BleueIssue accepts type='patch'."""
    issue = BleueIssue(id=1, description="Test issue", type="patch")
    assert issue.type == "patch"


def test_bleue_issue_type_invalid():
    """Test that BleueIssue rejects invalid type values."""
    with pytest.raises(ValueError):
        BleueIssue(id=1, description="Test issue", type="invalid")


def test_bleue_comment_creation():
    """Test basic BleueComment creation."""
    comment = BleueComment(issue_id=1, comment="Test comment")
    assert comment.issue_id == 1
    assert comment.comment == "Test comment"
    assert comment.id is None


def test_bleue_comment_trim() -> None:
    """Test comment whitespace trimming."""
    comment = BleueComment(issue_id=1, comment="  Test comment  ")
    assert comment.comment == "Test comment"


def test_bleue_comment_empty_validation() -> None:
    """Test that empty comment raises validation error."""
    with pytest.raises(ValidationError):
        BleueComment(issue_id=1, comment="")
