from typing import Literal, Optional, cast

from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import RadioButton, RadioSet, Static

from bleue.core.database import create_issue as db_create_issue
from bleue.tui.components.issue_form import IssueForm
from bleue.tui.screens.workflow_select_modal import WORKFLOW_OPTIONS
from bleue.tui.worker_utils import WORKER_OPTIONS


class CreateIssueModal(ModalScreen[Optional[int]]):
    """Modal form for creating new issues."""

    @staticmethod
    def _make_workflow_radio_id(workflow_value: Optional[str]) -> str:
        """Generate a radio button ID from a workflow value."""
        return f"workflow-{workflow_value}" if workflow_value else "workflow-none"

    @staticmethod
    def _make_worker_radio_id(worker_id: Optional[str]) -> str:
        """Generate a radio button ID from a worker ID."""
        return f"worker-{worker_id}" if worker_id else "worker-none"

    def compose(self) -> ComposeResult:
        """Create child widgets for the create issue modal."""
        workflow_buttons = [
            RadioButton(
                display_name,
                value=(workflow_value is None),
                id=self._make_workflow_radio_id(workflow_value),
            )
            for display_name, workflow_value in WORKFLOW_OPTIONS
        ]

        worker_buttons = [
            RadioButton(
                display_name,
                value=(worker_id is None),
                id=self._make_worker_radio_id(worker_id),
            )
            for display_name, worker_id in WORKER_OPTIONS
        ]

        yield Container(
            Static("Create New Issue", id="modal-header"),
            IssueForm(
                initial_title="Enter issue title ...",
                initial_text="Enter issue description ...",
                on_save_callback=self.handle_save,
                on_cancel_callback=self.handle_cancel,
            ),
            Static("Workflow", classes="selector-label"),
            RadioSet(*workflow_buttons, id="workflow-radioset"),
            Static("Worker", classes="selector-label"),
            RadioSet(*worker_buttons, id="worker-radioset"),
            id="modal-content",
        )

    def _get_selected_workflow(self) -> Optional[Literal["main", "patch"]]:
        """Extract the selected workflow value from the workflow RadioSet.

        Returns:
            The selected workflow value (None, 'main', or 'patch').
        """
        radioset = self.query_one("#workflow-radioset", RadioSet)
        selected_button = radioset.pressed_button

        if selected_button is None:
            return None

        id_to_workflow: dict[str, Optional[str]] = {
            self._make_workflow_radio_id(workflow_value): workflow_value
            for _, workflow_value in WORKFLOW_OPTIONS
        }

        button_id = selected_button.id
        value = id_to_workflow.get(button_id) if button_id else None
        return cast(Optional[Literal["main", "patch"]], value)

    def _get_selected_worker(self) -> Optional[str]:
        """Extract the selected worker value from the worker RadioSet.

        Returns:
            The selected worker ID or None for unassigned.
        """
        radioset = self.query_one("#worker-radioset", RadioSet)
        selected_button = radioset.pressed_button

        if selected_button is None:
            return None

        id_to_worker: dict[str, Optional[str]] = {
            self._make_worker_radio_id(worker_id): worker_id for _, worker_id in WORKER_OPTIONS
        }

        button_id = selected_button.id
        return id_to_worker.get(button_id) if button_id else None

    def handle_save(self, description: str, title: str) -> None:
        """Handle save action from IssueForm.

        Args:
            description: Validated description text
            title: Validated title text
        """
        workflow = self._get_selected_workflow()
        worker = self._get_selected_worker()
        self.create_issue_handler(description, title, workflow, worker)

    def handle_cancel(self) -> None:
        """Handle cancel action from IssueForm."""
        self.dismiss(None)

    @work(exclusive=True, thread=True)
    def create_issue_handler(
        self,
        description: str,
        title: str,
        workflow: Optional[Literal["main", "patch"]] = None,
        assigned_to: Optional[str] = None,
    ) -> None:
        """Create issue in background thread.

        Args:
            description: Issue description to save
            title: Issue title to save
            workflow: Optional workflow type (None, 'main', or 'patch')
            assigned_to: Optional worker ID to assign
        """
        try:
            issue = db_create_issue(
                description, title=title, workflow=workflow, assigned_to=assigned_to
            )
            self.app.call_from_thread(self.dismiss, issue.id)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error creating issue: {e}", severity="error")
