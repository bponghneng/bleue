import logging
from functools import partial
from typing import Literal, Optional

from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.coordinate import Coordinate
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Static,
)
from textual.widgets._data_table import RowKey

from bleue.core.database import (
    delete_issue,
    fetch_all_issues,
    update_issue_assignment,
    update_issue_workflow,
)
from bleue.core.models import BleueIssue
from bleue.tui.screens.confirm_delete_modal import ConfirmDeleteModal
from bleue.tui.screens.create_issue_modal import CreateIssueModal
from bleue.tui.screens.help_modal import HelpModal
from bleue.tui.screens.issue_detail_screen import IssueDetailScreen
from bleue.tui.screens.worker_assign_modal import WorkerAssignModal
from bleue.tui.screens.workflow_select_modal import (
    WorkflowSelection,
    WorkflowSelectModal,
)
from bleue.tui.worker_utils import get_worker_display_name

logger = logging.getLogger(__name__)


class IssueListScreen(Screen):
    """Main screen displaying issue list in DataTable."""

    BINDINGS = [
        ("n", "new_issue", "New"),
        ("v", "view_detail", "View"),
        ("enter", "view_detail", "View Details"),
        ("r", "refresh", "Refresh"),
        ("a", "assign_worker", "Assign"),
        ("w", "set_workflow", "Set Workflow"),
        ("d", "delete_issue", "Delete"),
        ("delete", "delete_issue", "Delete"),
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
    ]

    loading: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        """Create child widgets for the issue list screen."""
        yield Header(show_clock=True)
        yield Container(
            Static("Issues", id="content_header"),
            DataTable(
                id="issue_table",
                cell_padding=1,
                classes="table",
                header_height=2,
                zebra_stripes=True,
            ),
            Static("", id="content_footer"),
            id="content",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_column("ID")
        table.add_column("Title", width=35)
        table.add_column("Workflow", width=12)
        table.add_column("Worker")
        table.add_column("Status")
        self.load_issues()

    @work(exclusive=True, thread=True)
    def load_issues(self) -> None:
        """Load issues from database in background thread."""
        try:
            issues = fetch_all_issues()
            self.app.call_from_thread(self._populate_table, issues)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error loading issues: {e}", severity="error")

    def _populate_table(self, issues: list[BleueIssue]) -> None:
        """Populate the DataTable with issue data."""
        table = self.query_one(DataTable)
        table.clear()

        if not issues:
            self.notify("No issues found. Press 'n' to create one.", severity="information")
            return

        for issue in issues:
            assigned = get_worker_display_name(issue.assigned_to) or "None"
            workflow = issue.type.title() if issue.type else "None"

            table.add_row(
                str(issue.id),
                issue.title,
                workflow,
                assigned,
                issue.status,
                height=3,
                key=str(issue.id),
            )

    def action_new_issue(self) -> None:
        """Show the create issue modal."""
        self.app.push_screen(CreateIssueModal(), self.on_issue_created)

    def action_view_detail(self) -> None:
        """Navigate to issue detail screen."""
        table = self.query_one(DataTable)
        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No issue selected", severity="warning")
            return

        row_key = table.get_row_at(table.cursor_row)
        issue_id = int(row_key[0])
        self.app.push_screen(IssueDetailScreen(issue_id))

    def action_delete_issue(self) -> None:
        """Delete the selected issue after confirmation."""
        table = self.query_one(DataTable)
        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No issue selected", severity="warning")
            return

        # Get issue data from the table row
        row_data = table.get_row_at(table.cursor_row)
        issue_id = int(row_data[0])
        issue_title = str(row_data[1])
        issue_status = str(row_data[4])
        base_status = issue_status.split()[0] if issue_status else ""
        coordinate = Coordinate(row=table.cursor_row, column=0)
        row_key = table.coordinate_to_cell_key(coordinate).row_key
        if row_key is None:
            self.notify("Unable to determine selected issue", severity="error")
            return

        # Only allow deletion of pending issues
        if base_status != "pending":
            self.notify("Only pending issues can be deleted", severity="warning")
            return

        # Show confirmation modal with callback
        callback = partial(self.handle_delete_confirmation, issue_id, row_key)
        self.app.push_screen(ConfirmDeleteModal(issue_id, issue_title), callback)

    def handle_delete_confirmation(
        self, issue_id: int, row_key: RowKey, confirmed: Optional[bool]
    ) -> None:
        """Handle the result of delete confirmation."""
        if not confirmed:
            return

        # Perform deletion in background thread
        self.delete_issue_handler(issue_id, row_key)

    @work(exclusive=True, thread=True)
    def delete_issue_handler(self, issue_id: int, row_key: RowKey) -> None:
        """Delete issue in background thread."""
        try:
            delete_issue(issue_id)
            # Update UI from thread
            self.app.call_from_thread(
                self._remove_row_and_notify, row_key, f"Issue #{issue_id} deleted successfully"
            )
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error deleting issue: {e}", severity="error")

    def _remove_row_and_notify(self, row_key: RowKey, message: str) -> None:
        """Remove row from table and show notification (must be called from main thread)."""
        table = self.query_one(DataTable)
        table.remove_row(row_key)
        self.notify(message, severity="information")

    def action_help(self) -> None:
        """Show help screen."""
        self.app.push_screen(HelpModal())

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def on_issue_created(self, issue_id: Optional[int]) -> None:
        """Callback after issue creation."""
        if issue_id is not None:
            self.notify(f"Issue #{issue_id} created successfully", severity="information")
            self.load_issues()

    def action_assign_worker(self) -> None:
        """Open worker assignment modal for the selected issue."""
        table = self.query_one(DataTable)
        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No issue selected", severity="warning")
            return

        # Get issue data from the table row
        row_data = table.get_row_at(table.cursor_row)
        issue_id = int(row_data[0])
        issue_status = str(row_data[4])
        base_status = issue_status.split()[0] if issue_status else ""

        # Only allow assignment for pending issues
        if base_status != "pending":
            self.notify("Only pending issues can be assigned", severity="warning")
            return

        # Get current assignment from database - we need to fetch the actual issue
        # to get the worker_id, since the table only shows display names
        from bleue.core.database import fetch_issue

        try:
            current_issue = fetch_issue(issue_id)
            current_assignment = current_issue.assigned_to if current_issue else None
        except Exception as e:
            logger.warning(f"Failed to fetch current assignment for issue {issue_id}: {e}")
            current_assignment = None

        # Show worker assignment modal with callback
        callback = partial(self.handle_worker_assignment, issue_id)
        self.app.push_screen(WorkerAssignModal(current_assignment), callback)

    def action_set_workflow(self) -> None:
        """Open workflow selection modal for the selected issue."""
        table = self.query_one(DataTable)
        if table.cursor_row is None or table.cursor_row < 0:
            self.notify("No issue selected", severity="warning")
            return

        # Get issue data from the table row
        row_data = table.get_row_at(table.cursor_row)
        issue_id = int(row_data[0])
        issue_status = str(row_data[4])
        base_status = issue_status.split()[0] if issue_status else ""

        # Only allow workflow selection for pending issues
        if base_status != "pending":
            self.notify("Only pending issues can have workflow set", severity="warning")
            return

        # Fetch current workflow in background thread
        self._fetch_issue_worker(issue_id)

    @work(exclusive=True, thread=True)
    def _fetch_issue_worker(self, issue_id: int) -> None:
        """Fetch issue data in background thread and show workflow modal.

        Args:
            issue_id: The ID of the issue to fetch.
        """
        from bleue.core.database import fetch_issue

        current_workflow: Optional[str] = None
        try:
            current_issue = fetch_issue(issue_id)
            current_workflow = current_issue.type if current_issue else None
        except Exception as e:
            logger.warning(f"Failed to fetch current workflow for issue {issue_id}: {e}")
            current_workflow = None

        # Show modal on main thread - defer modal creation to main thread
        self.app.call_from_thread(self._push_workflow_modal, current_workflow, issue_id)

    def action_refresh(self) -> None:
        """Refresh the issue list."""
        self.load_issues()

    def _push_workflow_modal(self, current_workflow: Optional[str], issue_id: int) -> None:
        """Push workflow selection modal on main thread.

        Args:
            current_workflow: The current workflow value.
            issue_id: The ID of the issue to update.
        """
        callback = partial(self.handle_workflow_selection, issue_id)
        self.app.push_screen(WorkflowSelectModal(current_workflow), callback)

    def handle_workflow_selection(self, issue_id: int, selection: WorkflowSelection) -> None:
        """Handle the result of workflow selection modal.

        Args:
            issue_id: The ID of the issue to update.
            selection: The workflow selection result.
        """
        # Early return if cancelled
        if not selection.confirmed:
            return

        # Perform workflow update in background thread
        self.set_workflow_handler(issue_id, selection.value)

    @work(exclusive=True, thread=True)
    def set_workflow_handler(
        self, issue_id: int, workflow: Optional[Literal["main", "patch"]]
    ) -> None:
        """Set workflow on issue in background thread.

        Args:
            issue_id: The ID of the issue to update.
            workflow: The workflow to set (None for no workflow).
        """
        try:
            updated_issue = update_issue_workflow(issue_id, workflow)
            # Update UI from thread
            self.app.call_from_thread(self._update_workflow_success, updated_issue)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error setting workflow: {e}", severity="error")

    def _update_workflow_success(self, updated_issue: BleueIssue) -> None:
        """Show notification after successful workflow update.

        Args:
            updated_issue: The updated issue with new workflow.
        """
        workflow_display = updated_issue.type.title() if updated_issue.type else "None"

        # Find and update the workflow column in the table
        table = self.query_one(DataTable)
        issue_key = str(updated_issue.id)
        try:
            for row_index in range(len(table.rows)):
                row_data = table.get_row_at(row_index)
                if str(row_data[0]) == issue_key:
                    # Update the workflow column (index 2)
                    table.update_cell_at(Coordinate(row=row_index, column=2), workflow_display)
                    break
        except Exception as e:
            logger.error(f"Error updating table after workflow change: {e}")
            self.load_issues()

        if updated_issue.type:
            msg = f"Issue #{updated_issue.id} workflow set to {workflow_display}"
        else:
            msg = f"Issue #{updated_issue.id} workflow cleared"
        self.notify(msg, severity="information")

    def handle_worker_assignment(self, issue_id: int, assigned_to: Optional[str]) -> None:
        """Handle the result of worker assignment modal.

        Args:
            issue_id: The ID of the issue to assign.
            assigned_to: The selected worker ID (None for unassigned, or worker ID).
                        Returns None if modal was cancelled.
        """
        # Modal returns None if cancelled or if user didn't make a change
        # We need to distinguish between these cases
        # The modal always returns a value (the selected worker), so if it's None
        # it means either cancelled or unassigned was selected
        # For now, we'll proceed with the assignment

        # Perform assignment in background thread
        self.assign_worker_handler(issue_id, assigned_to)

    @work(exclusive=True, thread=True)
    def assign_worker_handler(self, issue_id: int, assigned_to: Optional[str]) -> None:
        """Assign worker to issue in background thread.

        Args:
            issue_id: The ID of the issue to assign.
            assigned_to: The worker ID to assign (None for unassigned).
        """
        try:
            updated_issue = update_issue_assignment(issue_id, assigned_to)
            # Update UI from thread
            self.app.call_from_thread(self._update_assignment_success, updated_issue)
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error assigning worker: {e}", severity="error")

    def _update_assignment_success(self, updated_issue: BleueIssue) -> None:
        """Update table row after successful assignment and show notification.

        Args:
            updated_issue: The updated issue with new assignment.
        """
        # Format assignment for display
        assigned_display = get_worker_display_name(updated_issue.assigned_to) or "None"
        worker_name = assigned_display if assigned_display != "None" else None

        # Find and update the row in the table
        table = self.query_one(DataTable)
        issue_key = str(updated_issue.id)

        # Update the row
        try:
            # Get the current row data
            for row_index in range(len(table.rows)):
                row_data = table.get_row_at(row_index)
                if str(row_data[0]) == issue_key:
                    # Update the assignment column (index 3)
                    table.update_cell_at(Coordinate(row=row_index, column=3), assigned_display)
                    break

            # Show success notification
            if worker_name:
                msg = f"Issue #{updated_issue.id} assigned to {worker_name}"
                self.notify(msg, severity="information")
            else:
                self.notify(f"Issue #{updated_issue.id} unassigned", severity="information")

        except Exception as e:
            logger.error(f"Error updating table after assignment: {e}")
            # Fall back to full reload
            self.load_issues()
