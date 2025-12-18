from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

from bleue.tui.components.confirm_delete_form import ConfirmDeleteForm


class ConfirmDeleteModal(ModalScreen[bool]):
    """Modal dialog for confirming issue deletion."""

    def __init__(self, issue_id: int, issue_title: str):
        """Initialize with issue ID and description.

        Args:
            issue_id: The ID of the issue to delete.
            issue_title: The issue description (will be truncated for display).
        """
        super().__init__()
        self.issue_id = issue_id
        self.issue_title = issue_title

    def compose(self) -> ComposeResult:
        """Create child widgets for the confirmation modal."""
        yield Container(
            Static(f"Delete Issue #{self.issue_id}", id="modal-header"),
            ConfirmDeleteForm(
                issue_id=self.issue_id,
                issue_title=self.issue_title,
                on_delete_callback=self.handle_delete,
                on_cancel_callback=self.handle_cancel,
            ),
            id="modal-content",
        )

    def handle_delete(self) -> None:
        """Handle delete action from ConfirmDeleteForm."""
        self.dismiss(True)

    def handle_cancel(self) -> None:
        """Handle cancel action from ConfirmDeleteForm."""
        self.dismiss(False)
