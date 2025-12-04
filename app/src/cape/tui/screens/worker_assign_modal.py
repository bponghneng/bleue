"""Worker assignment modal widget for Cape TUI."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, RadioButton, RadioSet, Static

# Worker options: (display_name, worker_id)
# Grouped by fleet: Alleycat, Nebuchadnezzar, Tydirium
WORKER_OPTIONS: list[tuple[str, str | None]] = [
    ("Unassigned", None),
    ("Alleycat 1 (alleycat-1)", "alleycat-1"),
    ("Alleycat 2 (alleycat-2)", "alleycat-2"),
    ("Alleycat 3 (alleycat-3)", "alleycat-3"),
    ("Nebuchadnezzar 1 (hailmary-1)", "hailmary-1"),
    ("Nebuchadnezzar 2 (hailmary-2)", "hailmary-2"),
    ("Nebuchadnezzar 3 (hailmary-3)", "hailmary-3"),
    ("Tydirium 1 (tydirium-1)", "tydirium-1"),
    ("Tydirium 2 (tydirium-2)", "tydirium-2"),
    ("Tydirium 3 (tydirium-3)", "tydirium-3"),
]

# Build lookup dictionary from worker_id to display name (without the worker_id suffix)
_WORKER_DISPLAY_NAMES: dict[str | None, str] = {}
for display_name, worker_id in WORKER_OPTIONS:
    if worker_id is None:
        _WORKER_DISPLAY_NAMES[None] = ""
    else:
        # Extract just the fleet name and number (e.g., "Alleycat 1" from "Alleycat 1 (alleycat-1)")
        name_part = display_name.split(" (")[0]
        _WORKER_DISPLAY_NAMES[worker_id] = name_part


def get_worker_display_name(worker_id: Optional[str]) -> str:
    """Get the display name for a worker ID.

    Args:
        worker_id: The worker ID (e.g., "alleycat-1", "hailmary-2") or None for unassigned.

    Returns:
        The display name (e.g., "Alleycat 1", "Nebuchadnezzar 2") or empty string for unassigned.
    """
    return _WORKER_DISPLAY_NAMES.get(worker_id, "")


class WorkerAssignModal(ModalScreen[Optional[str]]):
    """Modal for assigning an issue to a worker."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, current_assignment: Optional[str] = None):
        """Initialize the worker assignment modal.

        Args:
            current_assignment: The current worker assignment (e.g., None,
                'tydirium-1', 'alleycat-1').
        """
        super().__init__()
        self.current_assignment = current_assignment

    def _make_radio_id(self, worker_id: Optional[str]) -> str:
        """Generate a radio button ID from a worker ID."""
        return f"worker-{worker_id}" if worker_id else "worker-none"

    def compose(self) -> ComposeResult:
        """Create child widgets for the worker assignment modal."""
        # Dynamically generate RadioButtons from WORKER_OPTIONS
        radio_buttons = [
            RadioButton(
                display_name,
                value=(self.current_assignment == worker_id),
                id=self._make_radio_id(worker_id),
            )
            for display_name, worker_id in WORKER_OPTIONS
        ]

        yield Container(
            Static("Assign Worker", id="modal-header"),
            Static("Select a worker to assign this issue:", id="modal-description"),
            RadioSet(*radio_buttons, id="worker-radioset"),
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
            return

        # Build a lookup from radio button ID to worker_id
        id_to_worker = {
            self._make_radio_id(worker_id): worker_id for _, worker_id in WORKER_OPTIONS
        }

        # Look up the worker_id from the selected button's ID
        button_id = selected_button.id
        worker_id = id_to_worker.get(button_id) if button_id else None
        self.dismiss(worker_id)

    def action_cancel(self) -> None:
        """Cancel and close the modal without making changes."""
        self.dismiss(None)
