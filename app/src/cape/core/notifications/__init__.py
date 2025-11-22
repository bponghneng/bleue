"""Notification helpers for Cape workflows including progress comments and stream handlers.

This package provides utilities for inserting progress comments during
workflow execution and creating stream handlers for agent output processing.

Example:
    from cape.core.notifications import (
        insert_progress_comment,
        make_progress_comment_handler
    )

    # Insert a manual progress comment
    status, msg = insert_progress_comment(issue_id, "Starting implementation")
    logger.debug(msg) if status == "success" else logger.error(msg)

    # Create a stream handler for agent execution
    handler = make_progress_comment_handler(issue_id, adw_id, logger)
    agent.execute_prompt(request, stream_handler=handler)
"""

from cape.core.database import create_comment
from cape.core.notifications.agent_stream_handlers import (
    make_progress_comment_handler,
    make_simple_logger_handler,
)


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

    This is re-exported from the parent notifications module for
    backward compatibility.
    """
    try:
        comment = create_comment(issue_id, comment_text)
        return ("success", f"Comment inserted: ID={comment.id}, Text='{comment_text}'")
    except Exception as exc:  # pragma: no cover - logging path only
        return ("error", f"Failed to insert comment on issue {issue_id}: {exc}")

__all__ = [
    "insert_progress_comment",
    "make_progress_comment_handler",
    "make_simple_logger_handler",
]
