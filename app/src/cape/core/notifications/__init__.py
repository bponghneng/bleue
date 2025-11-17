"""Notification helpers for Cape workflows including progress comments and stream handlers.

This package provides utilities for inserting progress comments during
workflow execution and creating stream handlers for agent output processing.

Example:
    from cape.core.notifications import (
        insert_progress_comment,
        make_progress_comment_handler
    )

    # Insert a manual progress comment
    insert_progress_comment(issue_id, "Starting implementation", logger)

    # Create a stream handler for agent execution
    handler = make_progress_comment_handler(issue_id, adw_id, logger)
    agent.execute_prompt(request, stream_handler=handler)
"""

from cape.core.database import create_comment
from cape.core.notifications.agent_stream_handlers import (
    make_progress_comment_handler,
    make_simple_logger_handler,
)


def insert_progress_comment(issue_id: int, comment_text: str, logger) -> None:
    """Insert a progress comment for the given issue.

    Best-effort helper that logs the outcome but never raises, ensuring
    workflow execution continues even if Supabase is unavailable.

    This is re-exported from the parent notifications module for
    backward compatibility.
    """
    from logging import Logger

    try:
        comment = create_comment(issue_id, comment_text)
        logger.debug("Comment inserted: ID=%s, Text='%s'", comment.id, comment_text)
    except Exception as exc:  # pragma: no cover - logging path only
        logger.error("Failed to insert comment on issue %s: %s", issue_id, exc)

__all__ = [
    "insert_progress_comment",
    "make_progress_comment_handler",
    "make_simple_logger_handler",
]
