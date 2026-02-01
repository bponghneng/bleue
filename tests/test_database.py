"""Tests for database operations."""

from unittest.mock import Mock, patch

import pytest
from postgrest.exceptions import APIError

from bleue.core.database import (
    SupabaseConfig,
    create_comment,
    create_issue,
    delete_issue,
    fetch_all_issues,
    fetch_comments,
    fetch_issue,
    get_client,
    update_issue_assignment,
    update_issue_description,
    update_issue_status,
    update_issue_workflow,
)
from bleue.core.models import BleueComment


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")


def test_supabase_config_validation_success(mock_env) -> None:
    """Test config validation with valid env vars."""
    config = SupabaseConfig()
    config.validate()  # Should not raise


def test_supabase_config_validation_missing_url(monkeypatch) -> None:
    """Test config validation fails with missing URL."""
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test_key")

    config = SupabaseConfig()
    with pytest.raises(ValueError, match="SUPABASE_URL"):
        config.validate()


def test_supabase_config_validation_missing_key(monkeypatch) -> None:
    """Test config validation fails with missing key."""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    config = SupabaseConfig()
    with pytest.raises(ValueError, match="SUPABASE_SERVICE_ROLE_KEY"):
        config.validate()


@patch("bleue.core.database.create_client")
def test_get_client(mock_create_client, mock_env) -> None:
    """Test get_client creates and returns client."""
    mock_client = Mock()
    mock_create_client.return_value = mock_client

    # Clear cache and global client
    get_client.cache_clear()
    import bleue.core.database

    bleue.core.database._client = None

    client = get_client()
    assert client is mock_client
    mock_create_client.assert_called_once()


@patch("bleue.core.database.get_client")
def test_create_issue_success(mock_get_client) -> None:
    """Test successful issue creation."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "pending"}]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = create_issue("Test issue")
    assert issue.id == 1
    assert issue.description == "Test issue"
    assert issue.status == "pending"


@patch("bleue.core.database.get_client")
def test_create_issue_empty_description(_mock_get_client) -> None:
    """Test creating issue with empty description fails."""
    with pytest.raises(ValueError, match="cannot be empty"):
        create_issue("")


@patch("bleue.core.database.get_client")
def test_create_issue_whitespace_only(_mock_get_client) -> None:
    """Test creating issue with whitespace-only description fails."""
    with pytest.raises(ValueError, match="cannot be empty"):
        create_issue("   ")


@patch("bleue.core.database.get_client")
def test_create_issue_with_workflow_main(mock_get_client) -> None:
    """Test creating issue with workflow set to 'main'."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [
        {"id": 1, "description": "Test issue", "status": "pending", "type": "main"}
    ]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = create_issue("Test issue description text", workflow="main")
    assert issue.id == 1
    assert issue.type == "main"

    # Verify the insert payload includes the type field
    insert_data = mock_table.insert.call_args.args[0]
    assert insert_data["type"] == "main"


@patch("bleue.core.database.get_client")
def test_create_issue_with_workflow_patch(mock_get_client) -> None:
    """Test creating issue with workflow set to 'patch'."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [
        {"id": 1, "description": "Test issue", "status": "pending", "type": "patch"}
    ]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = create_issue("Test issue description text", workflow="patch")
    assert issue.id == 1
    assert issue.type == "patch"

    insert_data = mock_table.insert.call_args.args[0]
    assert insert_data["type"] == "patch"


@patch("bleue.core.database.get_client")
def test_create_issue_with_workflow_none(mock_get_client) -> None:
    """Test creating issue with workflow set to None (default)."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "pending"}]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = create_issue("Test issue description text", workflow=None)
    assert issue.id == 1

    # Verify the insert payload does NOT include the type field when workflow is None
    insert_data = mock_table.insert.call_args.args[0]
    assert "type" not in insert_data


@patch("bleue.core.database.get_client")
def test_create_issue_with_invalid_workflow(_mock_get_client) -> None:
    """Test creating issue with invalid workflow value raises ValueError."""
    with pytest.raises(ValueError, match="Invalid workflow"):
        create_issue("Test issue description text", workflow="invalid")


@patch("bleue.core.database.get_client")
def test_create_issue_with_worker(mock_get_client) -> None:
    """Test creating issue with a valid worker assignment."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [
        {
            "id": 1,
            "description": "Test issue",
            "status": "pending",
            "assigned_to": "executor-1",
        }
    ]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = create_issue("Test issue description text", assigned_to="executor-1")
    assert issue.id == 1
    assert issue.assigned_to == "executor-1"

    insert_data = mock_table.insert.call_args.args[0]
    assert insert_data["assigned_to"] == "executor-1"


@patch("bleue.core.database.get_client")
def test_create_issue_with_worker_none(mock_get_client) -> None:
    """Test creating issue with worker set to None (default)."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "pending"}]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = create_issue("Test issue description text", assigned_to=None)
    assert issue.id == 1

    # Verify the insert payload does NOT include assigned_to when it is None
    insert_data = mock_table.insert.call_args.args[0]
    assert "assigned_to" not in insert_data


@patch("bleue.core.database.get_client")
def test_create_issue_with_invalid_worker(_mock_get_client) -> None:
    """Test creating issue with invalid worker ID raises ValueError."""
    with pytest.raises(ValueError, match="Invalid worker ID"):
        create_issue("Test issue description text", assigned_to="invalid-worker")


@patch("bleue.core.database.get_client")
def test_create_issue_with_workflow_and_worker(mock_get_client) -> None:
    """Test creating issue with both workflow and worker parameters."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [
        {
            "id": 1,
            "description": "Test issue",
            "status": "pending",
            "type": "main",
            "assigned_to": "xwing-2",
        }
    ]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = create_issue(
        "Test issue description text", workflow="main", assigned_to="xwing-2"
    )
    assert issue.id == 1
    assert issue.type == "main"
    assert issue.assigned_to == "xwing-2"

    insert_data = mock_table.insert.call_args.args[0]
    assert insert_data["type"] == "main"
    assert insert_data["assigned_to"] == "xwing-2"


@patch("bleue.core.database.get_client")
def test_create_issue_with_all_valid_workers(mock_get_client) -> None:
    """Test creating issue with each valid worker ID."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_get_client.return_value = mock_client

    valid_worker_ids = [
        "alleycat-1",
        "alleycat-2",
        "alleycat-3",
        "executor-1",
        "executor-2",
        "executor-3",
        "local-1",
        "local-2",
        "local-3",
        "tydirium-1",
        "tydirium-2",
        "tydirium-3",
        "xwing-1",
        "xwing-2",
        "xwing-3",
    ]

    for worker_id in valid_worker_ids:
        mock_execute.data = [
            {
                "id": 1,
                "description": "Test issue",
                "status": "pending",
                "assigned_to": worker_id,
            }
        ]
        mock_insert.execute.return_value = mock_execute

        issue = create_issue("Test issue description text", assigned_to=worker_id)
        assert issue.assigned_to == worker_id


@patch("bleue.core.database.get_client")
def test_create_issue_rejects_invalid_worker_ids(_mock_get_client) -> None:
    """Test that create_issue rejects invalid worker IDs."""
    invalid_workers = [
        "alleycat-4",
        "executor-4",
        "local-4",
        "xwing-4",
        "hailmary-1",
        "unknown-1",
    ]

    for worker_id in invalid_workers:
        with pytest.raises(ValueError, match="Invalid worker ID"):
            create_issue("Test issue description text", assigned_to=worker_id)


@patch("bleue.core.database.get_client")
def test_fetch_issue_success(mock_get_client) -> None:
    """Test successful issue fetch."""
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_maybe_single = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.maybe_single.return_value = mock_maybe_single
    mock_execute.data = {"id": 1, "description": "Test issue", "status": "pending"}
    mock_maybe_single.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = fetch_issue(1)
    assert issue.id == 1
    assert issue.description == "Test issue"


@patch("bleue.core.database.get_client")
def test_fetch_issue_not_found(mock_get_client) -> None:
    """Test fetching non-existent issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_maybe_single = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.maybe_single.return_value = mock_maybe_single
    mock_execute.data = None
    mock_maybe_single.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="not found"):
        fetch_issue(999)


@patch("bleue.core.database.get_client")
def test_fetch_all_issues_success(mock_get_client) -> None:
    """Test fetching all issues."""
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_order = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.order.return_value = mock_order
    mock_execute.data = [
        {"id": 1, "description": "Issue 1", "status": "pending"},
        {"id": 2, "description": "Issue 2", "status": "completed"},
    ]
    mock_order.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issues = fetch_all_issues()
    assert len(issues) == 2
    assert issues[0].id == 1
    assert issues[1].id == 2


@patch("bleue.core.database.get_client")
def test_create_comment_success(mock_get_client) -> None:
    """Test successful comment creation."""
    mock_client = Mock()
    mock_table = Mock()
    mock_insert = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_execute.data = [
        {
            "id": 1,
            "issue_id": 1,
            "comment": "Test comment",
            "raw": {"test": "data"},
            "source": "test",
            "type": "unit",
        }
    ]
    mock_insert.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    comment_payload = BleueComment(
        issue_id=1,
        comment="Test comment",
        raw={"test": "data"},
        source="test",
        type="unit",
    )

    comment = create_comment(comment_payload)
    assert comment.issue_id == 1
    assert comment.comment == "Test comment"
    assert comment.raw == {"test": "data"}
    assert comment.source == "test"
    assert comment.type == "unit"


@patch("bleue.core.database.get_client")
def test_fetch_comments_success(mock_get_client) -> None:
    """Test fetching comments for an issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_select = Mock()
    mock_eq = Mock()
    mock_order = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_eq
    mock_eq.order.return_value = mock_order
    mock_execute.data = [
        {"id": 1, "issue_id": 1, "comment": "Comment 1"},
        {"id": 2, "issue_id": 1, "comment": "Comment 2"},
    ]
    mock_order.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    comments = fetch_comments(1)
    assert len(comments) == 2
    assert comments[0].comment == "Comment 1"
    assert comments[1].comment == "Comment 2"


@patch("bleue.core.database.get_client")
def test_update_issue_status_success(mock_get_client) -> None:
    """Test successful status update."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "started"}]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_status(1, "started")
    assert issue.id == 1
    assert issue.status == "started"
    mock_table.update.assert_called_once_with({"status": "started"})


@patch("bleue.core.database.get_client")
def test_update_issue_status_to_completed(mock_get_client) -> None:
    """Test updating status to completed."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "completed"}]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_status(1, "completed")
    assert issue.status == "completed"


@patch("bleue.core.database.get_client")
def test_update_issue_status_invalid_status(_mock_get_client) -> None:
    """Test updating with invalid status fails."""
    with pytest.raises(ValueError, match="Invalid status"):
        update_issue_status(1, "invalid_status")


@patch("bleue.core.database.get_client")
def test_update_issue_status_not_found(mock_get_client) -> None:
    """Test updating non-existent issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = None
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="not found"):
        update_issue_status(999, "started")


@patch("bleue.core.database.get_client")
def test_update_issue_description_success(mock_get_client) -> None:
    """Test successful description update."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [{"id": 1, "description": "Updated description", "status": "pending"}]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_description(1, "Updated description")
    assert issue.id == 1
    assert issue.description == "Updated description"
    mock_table.update.assert_called_once_with({"description": "Updated description"})


@patch("bleue.core.database.get_client")
def test_update_issue_description_empty(_mock_get_client) -> None:
    """Test updating with empty description fails."""
    with pytest.raises(ValueError, match="cannot be empty"):
        update_issue_description(1, "")


@patch("bleue.core.database.get_client")
def test_update_issue_description_whitespace_only(_mock_get_client) -> None:
    """Test updating with whitespace-only description fails."""
    with pytest.raises(ValueError, match="cannot be empty"):
        update_issue_description(1, "   ")


@patch("bleue.core.database.get_client")
def test_update_issue_description_too_short(_mock_get_client) -> None:
    """Test updating with too short description fails."""
    with pytest.raises(ValueError, match="at least 10 characters"):
        update_issue_description(1, "Short")


@patch("bleue.core.database.get_client")
def test_update_issue_description_too_long(_mock_get_client) -> None:
    """Test updating with too long description fails."""
    long_description = "x" * 10001
    with pytest.raises(ValueError, match="cannot exceed 10000 characters"):
        update_issue_description(1, long_description)


@patch("bleue.core.database.get_client")
def test_update_issue_description_not_found(mock_get_client) -> None:
    """Test updating description of non-existent issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = None
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="not found"):
        update_issue_description(999, "Valid description text here")


@patch("bleue.core.database.get_client")
def test_delete_issue_success(mock_get_client) -> None:
    """Test successful issue deletion."""
    mock_client = Mock()
    mock_table = Mock()
    mock_delete = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.delete.return_value = mock_delete
    mock_delete.eq.return_value = mock_eq
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "pending"}]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    result = delete_issue(1)
    assert result is True
    mock_table.delete.assert_called_once()
    mock_delete.eq.assert_called_once_with("id", 1)


@patch("bleue.core.database.get_client")
def test_delete_issue_not_found(mock_get_client) -> None:
    """Test deleting non-existent issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_delete = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.delete.return_value = mock_delete
    mock_delete.eq.return_value = mock_eq
    mock_execute.data = None
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="not found"):
        delete_issue(999)


@patch("bleue.core.database.get_client")
def test_delete_issue_with_comments(mock_get_client) -> None:
    """Test deleting issue cascades to comments.

    Note: This test verifies the delete operation is called correctly.
    The actual cascade delete behavior is handled by the database
    foreign key constraint with ON DELETE CASCADE.
    """
    mock_client = Mock()
    mock_table = Mock()
    mock_delete = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.delete.return_value = mock_delete
    mock_delete.eq.return_value = mock_eq
    # Simulate successful deletion of issue with comments
    mock_execute.data = [{"id": 1, "description": "Issue with comments", "status": "pending"}]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    result = delete_issue(1)
    assert result is True
    # Verify that delete was called on the issues table
    mock_table.delete.assert_called_once()
    # The cascade to comments is handled by the database, not in application code


@patch("bleue.core.database.fetch_issue")
@patch("bleue.core.database.get_client")
def test_update_issue_assignment_success(mock_get_client, mock_fetch_issue) -> None:
    """Test successful worker assignment."""
    # Mock fetch_issue to return a pending issue
    mock_issue = Mock()
    mock_issue.status = "pending"
    mock_fetch_issue.return_value = mock_issue

    # Mock the database client
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [
        {
            "id": 1,
            "description": "Test issue",
            "status": "pending",
            "assigned_to": "executor-1",
        }
    ]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_assignment(1, "executor-1")
    assert issue.id == 1, "expected issue.id to be 1"
    assert issue.assigned_to == "executor-1", "expected assigned_to to be 'executor-1'"
    assert mock_table.update.call_count == 1, "expected mock_table.update to be called once"
    assert mock_table.update.call_args.args[0] == {
        "assigned_to": "executor-1"
    }, "expected mock_table.update called with assigned_to payload"


@patch("bleue.core.database.fetch_issue")
@patch("bleue.core.database.get_client")
def test_update_issue_assignment_to_none(mock_get_client, mock_fetch_issue) -> None:
    """Test unassigning a worker (setting to None)."""
    # Mock fetch_issue to return a pending issue
    mock_issue = Mock()
    mock_issue.status = "pending"
    mock_fetch_issue.return_value = mock_issue

    # Mock the database client
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [
        {
            "id": 1,
            "description": "Test issue",
            "status": "pending",
            "assigned_to": None,
        }
    ]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_assignment(1, None)
    assert issue.id == 1
    assert issue.assigned_to is None
    mock_table.update.assert_called_once_with({"assigned_to": None})


@patch("bleue.core.database.fetch_issue")
def test_update_issue_assignment_rejects_started_issue(mock_fetch_issue) -> None:
    """Test that assignment is rejected for started issues."""
    # Mock fetch_issue to return a started issue
    mock_issue = Mock()
    mock_issue.status = "started"
    mock_fetch_issue.return_value = mock_issue

    with pytest.raises(ValueError, match="Only pending issues can be assigned"):
        update_issue_assignment(1, "executor-1")


@patch("bleue.core.database.fetch_issue")
def test_update_issue_assignment_rejects_completed_issue(mock_fetch_issue) -> None:
    """Test that assignment is rejected for completed issues."""
    # Mock fetch_issue to return a completed issue
    mock_issue = Mock()
    mock_issue.status = "completed"
    mock_fetch_issue.return_value = mock_issue

    with pytest.raises(ValueError, match="Only pending issues can be assigned"):
        update_issue_assignment(1, "alleycat-1")


@patch("bleue.core.database.get_client")
def test_update_issue_assignment_rejects_invalid_worker(_mock_get_client) -> None:
    """Test that assignment is rejected for invalid worker IDs."""
    with pytest.raises(ValueError, match="Invalid worker ID"):
        update_issue_assignment(1, "invalid-worker")


@patch("bleue.core.database.fetch_issue")
def test_update_issue_assignment_nonexistent_issue(mock_fetch_issue) -> None:
    """Test assignment fails for non-existent issue."""
    mock_fetch_issue.side_effect = ValueError("Issue not found")

    with pytest.raises(ValueError, match="Failed to fetch issue"):
        update_issue_assignment(999, "executor-1")


@patch("bleue.core.database.fetch_issue")
@patch("bleue.core.database.get_client")
def test_update_issue_assignment_new_workers(mock_get_client, mock_fetch_issue) -> None:
    """Test assignment to new expanded worker pool IDs."""
    # Mock fetch_issue to return a pending issue
    mock_issue = Mock()
    mock_issue.status = "pending"
    mock_fetch_issue.return_value = mock_issue

    # Mock the database client
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_get_client.return_value = mock_client

    # Test all new worker IDs (executor and xwing series)
    new_worker_ids = [
        "executor-1",
        "executor-2",
        "executor-3",
        "tydirium-1",
        "tydirium-2",
        "tydirium-3",
        "xwing-1",
        "xwing-2",
        "xwing-3",
    ]

    for worker_id in new_worker_ids:
        mock_execute.data = [
            {
                "id": 1,
                "description": "Test issue",
                "status": "pending",
                "assigned_to": worker_id,
            }
        ]
        mock_eq.execute.return_value = mock_execute

        issue = update_issue_assignment(1, worker_id)
        assert issue.assigned_to == worker_id


@patch("bleue.core.database.get_client")
def test_update_issue_assignment_rejects_invalid_new_worker(_mock_get_client) -> None:
    """Test that assignment is rejected for invalid worker IDs not in expanded pool."""
    invalid_workers = [
        "alleycat-4",
        "local-4",
        "executor-4",
        "xwing-4",
        "hailmary-1",  # Old worker ID no longer valid
        "unknown-1",
    ]

    for worker_id in invalid_workers:
        with pytest.raises(ValueError, match="Invalid worker ID"):
            update_issue_assignment(1, worker_id)


@patch("bleue.core.database.get_client")
def test_update_issue_workflow_main(mock_get_client) -> None:
    """Test successful workflow update to 'main'."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [
        {"id": 1, "description": "Test issue", "status": "pending", "type": "main"}
    ]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_workflow(1, "main")
    assert issue.id == 1, "Expected issue ID to match the updated issue"
    assert issue.type == "main", "Expected workflow type to be updated to 'main'"
    mock_table.update.assert_called_once_with({"type": "main"})


@patch("bleue.core.database.get_client")
def test_update_issue_workflow_patch(mock_get_client) -> None:
    """Test successful workflow update to 'patch'."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [
        {"id": 2, "description": "Test issue", "status": "started", "type": "patch"}
    ]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_workflow(2, "patch")
    assert issue.id == 2, "Expected issue ID to match the updated issue"
    assert issue.type == "patch", "Expected workflow type to be updated to 'patch'"
    mock_table.update.assert_called_once_with({"type": "patch"})


@patch("bleue.core.database.get_client")
def test_update_issue_workflow_none(mock_get_client) -> None:
    """Test clearing workflow by setting to None."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = [{"id": 1, "description": "Test issue", "status": "pending", "type": None}]
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    issue = update_issue_workflow(1, None)
    assert issue.id == 1, "Expected issue ID to match the updated issue"
    assert issue.type is None, "Expected workflow type to be cleared (None)"
    mock_table.update.assert_called_once_with({"type": None})


@patch("bleue.core.database.get_client")
def test_update_issue_workflow_invalid(_mock_get_client) -> None:
    """Test updating with invalid workflow value fails."""
    with pytest.raises(ValueError, match="Invalid workflow"):
        update_issue_workflow(1, "invalid_workflow")


@patch("bleue.core.database.get_client")
def test_update_issue_workflow_not_found(mock_get_client) -> None:
    """Test updating workflow for non-existent issue."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()
    mock_execute = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_execute.data = None
    mock_eq.execute.return_value = mock_execute
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="not found"):
        update_issue_workflow(999, "main")


@patch("bleue.core.database.get_client")
def test_update_issue_workflow_database_error(mock_get_client) -> None:
    """Test handling of database API errors during workflow update."""
    mock_client = Mock()
    mock_table = Mock()
    mock_update = Mock()
    mock_eq = Mock()

    mock_client.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_eq.execute.side_effect = APIError(
        {"message": "DB connection failed", "code": "500", "details": "", "hint": ""}
    )
    mock_get_client.return_value = mock_client

    with pytest.raises(ValueError, match="Failed to update issue"):
        update_issue_workflow(1, "patch")
