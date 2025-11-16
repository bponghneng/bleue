"""
File system watcher for workflow state changes.

This module provides event-driven monitoring of workflow state files
using the watchdog library.
"""

import time
from pathlib import Path
from typing import Callable, Dict, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from cape.core.paths import CapePaths


class StateFileEventHandler(FileSystemEventHandler):
    """Handle file system events for state files."""

    def __init__(self):
        super().__init__()
        self.callbacks: Dict[str, Callable[[str], None]] = {}
        self.last_event_time: Dict[str, float] = {}
        self.debounce_interval = 0.1  # 100ms debounce window

    def register_callback(self, workflow_id: str, callback: Callable[[str], None]) -> None:
        """
        Register a callback for state file changes.

        Args:
            workflow_id: Workflow ID to monitor
            callback: Function to call when state file changes
        """
        self.callbacks[workflow_id] = callback

    def unregister_callback(self, workflow_id: str) -> None:
        """
        Unregister a callback for a workflow.

        Args:
            workflow_id: Workflow ID to stop monitoring
        """
        self.callbacks.pop(workflow_id, None)
        self.last_event_time.pop(workflow_id, None)

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        # Check if this is a state file
        if not event.src_path.endswith(".json"):
            return

        # Extract workflow ID from filename
        workflow_id = Path(event.src_path).stem

        # Check if we have a callback for this workflow
        callback = self.callbacks.get(workflow_id)
        if not callback:
            return

        # Debounce: ignore events that are too close together
        current_time = time.time()
        last_time = self.last_event_time.get(workflow_id, 0)

        if current_time - last_time < self.debounce_interval:
            return

        self.last_event_time[workflow_id] = current_time

        # Call the callback
        try:
            callback(workflow_id)
        except Exception:
            # Silently ignore callback errors to prevent observer from stopping
            pass


class StateWatcher:
    """Watch workflow state files for changes."""

    def __init__(self):
        """Initialize the state watcher."""
        self.event_handler = StateFileEventHandler()
        self.observer: Optional[Observer] = None

    def register_callback(self, workflow_id: str, callback: Callable[[str], None]) -> None:
        """
        Register a callback for workflow state changes.

        Args:
            workflow_id: Workflow ID to monitor
            callback: Function to call when state changes (receives workflow_id)
        """
        self.event_handler.register_callback(workflow_id, callback)

    def unregister_callback(self, workflow_id: str) -> None:
        """
        Unregister a callback for a workflow.

        Args:
            workflow_id: Workflow ID to stop monitoring
        """
        self.event_handler.unregister_callback(workflow_id)

    def start(self) -> None:
        """Start watching for state file changes."""
        if self.observer is not None and self.observer.is_alive():
            return  # Already started

        # Ensure state directory exists
        CapePaths.ensure_directories()
        state_dir = CapePaths.get_base_dir() / "state"
        state_dir.mkdir(parents=True, exist_ok=True)

        # Create observer and start watching
        self.observer = Observer()
        self.observer.schedule(self.event_handler, str(state_dir), recursive=False)
        self.observer.start()

    def stop(self) -> None:
        """Stop watching for state file changes."""
        if self.observer is None:
            return

        self.observer.stop()
        self.observer.join(timeout=5.0)
        self.observer = None

    def is_running(self) -> bool:
        """Check if the watcher is running."""
        return self.observer is not None and self.observer.is_alive()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
