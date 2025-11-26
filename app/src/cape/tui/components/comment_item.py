"""Individual comment item components for the TUI."""

import json
from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Collapsible, Static

if TYPE_CHECKING:
    from cape.core.models import CapeComment


def _parse_raw(raw: Any) -> dict:
    """Parse raw field, handling both dict and JSON string."""
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


class CommentHeader(Horizontal):
    """Header component for comments with timestamp and badges."""

    DEFAULT_CSS = """
    CommentHeader {
        height: auto;
        width: 100%;
    }
    """

    def __init__(self, timestamp: str, source: str | None, comment_type: str | None, **kwargs):
        """Initialize the comment header.

        Args:
            timestamp: Formatted timestamp string
            source: Comment source (e.g., "agent", "system")
            comment_type: Comment type (e.g., "claude", "artifact")
            **kwargs: Additional arguments passed to Horizontal
        """
        super().__init__(**kwargs)
        self.timestamp = timestamp
        self.source = source or "unknown"
        self.comment_type = comment_type or "unknown"

    def compose(self) -> ComposeResult:
        """Compose the header with timestamp and badges."""
        yield Static(f"[dim]{self.timestamp}[/dim]", classes="comment-timestamp")
        yield Static(
            f"[white on rgb(217,119,6)] {self.source} [/]",
            classes="comment-badge comment-badge-source",
        )
        yield Static(
            f"[white on purple] {self.comment_type} [/]",
            classes="comment-badge comment-badge-type",
        )
        yield Static("", classes="comment-header-spacer")


class CommentItem(Container):
    """Base component for rendering a single comment."""

    # CSS class for styling - override in subclasses
    DEFAULT_CLASSES = "comment-item"

    def __init__(self, comment: "CapeComment", **kwargs):
        """Initialize the comment item.

        Args:
            comment: The CapeComment to render
            **kwargs: Additional arguments passed to Container
        """
        # Merge subclass classes with any passed in kwargs
        classes = kwargs.pop("classes", "")
        combined_classes = f"{self.DEFAULT_CLASSES} {classes}".strip()
        super().__init__(classes=combined_classes, **kwargs)
        self.comment = comment

    def _get_timestamp(self) -> str:
        """Get formatted timestamp string."""
        return (
            self.comment.created_at.strftime("%Y-%m-%d %H:%M")
            if self.comment.created_at
            else "Unknown"
        )

    def _compose_header(self) -> CommentHeader:
        """Create the comment header component."""
        return CommentHeader(
            timestamp=self._get_timestamp(),
            source=self.comment.source,
            comment_type=self.comment.type,
        )

    def compose(self) -> ComposeResult:
        """Compose the comment layout."""
        yield self._compose_header()
        yield Static(self.comment.comment, classes="comment-body")


class AgentClaudeComment(CommentItem):
    """Comment from Claude agent.

    Supports two raw.type layouts:
    - "text": Displays raw.text content
    - "tool_use": Displays raw.input.todos as a checklist
    """

    DEFAULT_CLASSES = "comment-item agent-comment agent-claude"

    # Status emoji mapping
    _STATUS_EMOJI = {
        "completed": "✅",
        "in_progress": "🚀",
        "pending": "⏳",
    }

    def compose(self) -> ComposeResult:
        """Compose the comment layout based on raw.type."""
        yield self._compose_header()

        raw = _parse_raw(self.comment.raw)
        raw_type = raw.get("type")

        content_yielded = False

        if raw_type == "text":
            # Display text content from raw.text
            text = raw.get("text", "")
            if text:
                yield Static(text, classes="comment-body")
                content_yielded = True
        elif raw_type == "tool_use":
            # Display todos as checklist from raw.input.todos
            todos = raw.get("input", {}).get("todos", [])
            if todos:
                for todo in todos:
                    status = todo.get("status", "pending")
                    content = todo.get("content", "")
                    emoji = self._STATUS_EMOJI.get(status, "⏳")
                    yield Static(f"{emoji} {content}", classes="comment-todo-item")
                content_yielded = True

        # Always fall back to comment body if no content was rendered
        if not content_yielded and self.comment.comment:
            yield Static(self.comment.comment, classes="comment-body")


class AgentOpencodeComment(CommentItem):
    """Comment from OpenCode agent."""

    DEFAULT_CLASSES = "comment-item agent-comment agent-opencode"


class SystemArtifactComment(CommentItem):
    """System comment for artifacts.

    Displays the raw JSON content in a collapsible section.
    """

    DEFAULT_CLASSES = "comment-item system-comment system-artifact"

    def compose(self) -> ComposeResult:
        """Compose the artifact comment layout."""
        yield self._compose_header()

        raw = _parse_raw(self.comment.raw)
        raw_json = json.dumps(raw, indent=2)

        yield Collapsible(
            Static(raw_json, classes="comment-artifact-content"),
            title="Artifact",
            collapsed=True,
        )


class SystemWorkflowComment(CommentItem):
    """System comment for workflow events."""

    DEFAULT_CLASSES = "comment-item system-comment system-workflow"


class DefaultComment(CommentItem):
    """Default comment for unrecognized source-type combinations."""

    DEFAULT_CLASSES = "comment-item default-comment"


# Registry mapping (source, type) tuples to component classes
_COMMENT_TYPE_MAP: dict[tuple[str | None, str | None], type[CommentItem]] = {
    ("agent", "claude"): AgentClaudeComment,
    ("agent", "opencode"): AgentOpencodeComment,
    ("system", "artifact"): SystemArtifactComment,
    ("system", "workflow"): SystemWorkflowComment,
}


def create_comment_widget(comment: "CapeComment") -> CommentItem:
    """Factory to create appropriate comment widget based on source and type.

    Args:
        comment: The CapeComment to create a widget for

    Returns:
        A CommentItem subclass instance appropriate for the comment type
    """
    key = (comment.source, comment.type)
    widget_class = _COMMENT_TYPE_MAP.get(key, DefaultComment)
    return widget_class(comment)
