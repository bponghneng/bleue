"""Notification helpers for Cape workflow events."""

from logging import Logger

from cape.core.database import create_comment


def insert_progress_comment(issue_id: int, comment_text: str, logger: Logger) -> None:
    """Insert a progress comment for the given issue.

    Best-effort helper that logs the outcome but never raises, ensuring
    workflow execution continues even if Supabase is unavailable.
    """
    try:
        comment = create_comment(issue_id, comment_text)
        logger.debug("Comment inserted: ID=%s, Text='%s'", comment.id, comment_text)
    except Exception as exc:  # pragma: no cover - logging path only
        logger.error("Failed to insert comment on issue %s: %s", issue_id, exc)
