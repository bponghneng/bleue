"""Worker assignment modal widget for Cape TUI."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, RadioButton, RadioSet, Static

# Worker options: (display_name, worker_id)
WORKER_OPTIONS = [
    ("Unassigned", None),
    ("Tydirium (tydirium-1)", "tydirium-1"),
    ("Alleycat (alleycat-1)", "alleycat-1"),
]


class WorkerAssignModal(ModalScreen[Optional[str]]):
    """Modal for assigning an issue to a worker."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, current_assignment: Optional[str] = None):
        """Initialize the worker assignment modal.

        Args:
            current_assignment: The current worker assignment (None, 'tydirium-1', or 'alleycat-1').
        """
        super().__init__()
        self.current_assignment = current_assignment

    def compose(self) -> ComposeResult:
        """Create child widgets for the worker assignment modal."""
        yield Container(
            Static("Assign Worker", id="modal-header"),
            Static("Select a worker to assign this issue:", id="modal-description"),
            RadioSet(
                RadioButton(
                    "Unassigned", value=(self.current_assignment is None), id="worker-none"
                ),
                RadioButton(
                    "Tydirium (tydirium-1)",
                    value=(self.current_assignment == "tydirium-1"),
                    id="worker-tydirium-1",
                ),
                RadioButton(
                    "Alleycat (alleycat-1)",
                    value=(self.current_assignment == "alleycat-1"),
                    id="worker-alleycat-1",
                ),
                id="worker-radioset",
            ),
            Horizontal(
                Button("Save", variant="success", compact=True, flat=True, id="save-btn"),
                Button("Cancel", variant="error", compact=True, flat=True, id="cancel-btn"),
                id="button-row",
            ),
            id="modal-content",
        )

    def on_mount(self) -> None:
        """Initialize the modal when mounted - focus on selected radio button."""
        radioset = self.query_one("#worker-radioset", RadioSet)
        selected_button = radioset.pressed_button

        if selected_button is not None:
            # Focus on the currently selected radio button
            selected_button.focus()
        else:
            # If no selection, focus on the first radio button
            first_button = self.query_one("#worker-none", RadioButton)
            first_button.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "save-btn":
            self.action_save()
        elif button_id == "cancel-btn":
            self.action_cancel()

    def action_save(self) -> None:
        """Save the selected worker assignment."""
        # Get the selected radio button
        radioset = self.query_one("#worker-radioset", RadioSet)
        selected_button = radioset.pressed_button

        if selected_button is None:
            # No selection, return None (unassigned)
            self.dismiss(None)
        elif selected_button.id == "worker-none":
            self.dismiss(None)
        elif selected_button.id == "worker-tydirium-1":
            self.dismiss("tydirium-1")
        elif selected_button.id == "worker-alleycat-1":
            self.dismiss("alleycat-1")
        else:
            # Fallback
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel and close the modal without making changes."""
        self.dismiss(None)
