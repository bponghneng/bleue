"""Workflow selection modal widget for Bleue TUI."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, RadioButton, RadioSet, Static

# Workflow options: (display_name, workflow_value)
WORKFLOW_OPTIONS: list[tuple[str, str | None]] = [
    ("None", None),
    ("Main", "main"),
    ("Patch", "patch"),
]


class WorkflowSelectModal(ModalScreen[Optional[str]]):
    """Modal for selecting a workflow for an issue."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, current_workflow: Optional[str] = None):
        """Initialize the workflow selection modal.

        Args:
            current_workflow: The current workflow value (e.g., None, 'main', 'patch').
        """
        super().__init__()
        self.current_workflow = current_workflow

    def _make_radio_id(self, workflow_value: Optional[str]) -> str:
        """Generate a radio button ID from a workflow value."""
        return f"workflow-{workflow_value}" if workflow_value else "workflow-none"

    def compose(self) -> ComposeResult:
        """Create child widgets for the workflow selection modal."""
        radio_buttons = [
            RadioButton(
                display_name,
                value=(self.current_workflow == workflow_value),
                id=self._make_radio_id(workflow_value),
            )
            for display_name, workflow_value in WORKFLOW_OPTIONS
        ]

        yield Container(
            Static("Select Workflow", id="modal-header"),
            Static("Choose a workflow for this issue:", id="modal-description"),
            RadioSet(*radio_buttons, id="workflow-radioset"),
            Horizontal(
                Button("Save", variant="success", compact=True, flat=True, id="save-btn"),
                Button("Cancel", variant="error", compact=True, flat=True, id="cancel-btn"),
                id="button-row",
            ),
            id="modal-content",
        )

    def on_mount(self) -> None:
        """Initialize the modal when mounted - focus on selected radio button."""
        radioset = self.query_one("#workflow-radioset", RadioSet)
        selected_button = radioset.pressed_button

        if selected_button is not None:
            selected_button.focus()
        else:
            first_button = self.query_one("#workflow-none", RadioButton)
            first_button.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "save-btn":
            self.action_save()
        elif button_id == "cancel-btn":
            self.action_cancel()

    def action_save(self) -> None:
        """Save the selected workflow."""
        radioset = self.query_one("#workflow-radioset", RadioSet)
        selected_button = radioset.pressed_button

        if selected_button is None:
            self.dismiss(None)
            return

        # Build a lookup from radio button ID to workflow value
        id_to_workflow = {
            self._make_radio_id(workflow_value): workflow_value
            for _, workflow_value in WORKFLOW_OPTIONS
        }

        # Look up the workflow value from the selected button's ID
        button_id = selected_button.id
        workflow_value = id_to_workflow.get(button_id) if button_id else None
        self.dismiss(workflow_value)

    def action_cancel(self) -> None:
        """Cancel and close the modal without making changes."""
        self.dismiss(None)
