"""Notification helpers for Cape workflow events."""

from cape.core.database import create_comment


def insert_progress_comment(issue_id: int, comment_text: str) -> tuple[str, str]:
    """Insert a progress comment for the given issue.

    Best-effort helper that returns a status tuple, allowing callers to
    decide how to handle logging. Never raises, ensuring workflow execution
    continues even if Supabase is unavailable.

    Args:
        issue_id: The ID of the issue to add the comment to.
        comment_text: The text content of the comment.

    Returns:
        A tuple of (status, message) where status is "success" or "error"
        and message contains details about the operation result.
    """
    try:
        comment = create_comment(issue_id, comment_text)
        return ("success", f"Comment inserted: ID={comment.id}, Text='{comment_text}'")
    except Exception as exc:  # pragma: no cover - logging path only
        return ("error", f"Failed to insert comment on issue {issue_id}: {exc}")
