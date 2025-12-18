from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Static


class ConfirmDeleteForm(Container):
    """Reusable form component for confirming deletions.

    This composite widget provides a consistent confirmation interface
    for delete operations with cancel and delete buttons.

    Args:
        issue_id: The ID of the issue to delete
        issue_title: The issue title (will be truncated for display)
        on_delete_callback: Callable to invoke when delete is confirmed
        on_cancel_callback: Callable to invoke when cancel is triggered
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        issue_id: int,
        issue_title: str,
        on_delete_callback=None,
        on_cancel_callback=None,
    ):
        """Initialize the form with issue details and callbacks."""
        super().__init__()
        self.issue_id = issue_id
        self.issue_title = issue_title
        self.on_delete_callback = on_delete_callback
        self.on_cancel_callback = on_cancel_callback

    def compose(self) -> ComposeResult:
        """Create child widgets for the form."""
        # Truncate description if too long
        display_title = self.issue_title[:100]
        if len(self.issue_title) > 100:
            display_title += "..."

        yield Container(
            Static("Issue Title", id="delete-issue-title-label"),
            Static(display_title, id="delete-issue-title-text"),
            Static("⚠️  This action cannot be undone", id="delete-warning"),
            Horizontal(
                Button("Cancel", variant="default", compact=True, flat=True, id="cancel-btn"),
                Button("Delete", variant="error", compact=True, flat=True, id="delete-btn"),
                id="button-row",
            ),
            id="confirm-delete-form",
        )

    def on_mount(self) -> None:
        """Initialize the form when mounted - focus on cancel button."""
        cancel_btn = self.query_one("#cancel-btn", Button)
        cancel_btn.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "delete-btn":
            self.action_delete()
        elif event.button.id == "cancel-btn":
            self.action_cancel()

    def action_delete(self) -> None:
        """Trigger delete callback."""
        if self.on_delete_callback:
            self.on_delete_callback()

    def action_cancel(self) -> None:
        """Trigger cancel callback."""
        if self.on_cancel_callback:
            self.on_cancel_callback()
