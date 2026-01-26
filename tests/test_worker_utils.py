"""Tests for TUI worker utilities."""

from bleue.tui.worker_utils import WORKER_OPTIONS, get_worker_display_name


class TestWorkerOptions:
    """Tests for WORKER_OPTIONS constant."""

    def test_worker_options_structure(self):
        """Test WORKER_OPTIONS has correct structure."""
        assert isinstance(WORKER_OPTIONS, list)
        assert len(WORKER_OPTIONS) > 0

        # Check each entry is a tuple with (display_name, worker_id)
        for entry in WORKER_OPTIONS:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            display_name, worker_id = entry
            assert isinstance(display_name, str)
            assert worker_id is None or isinstance(worker_id, str)

    def test_worker_options_includes_all_workers(self):
        """Test WORKER_OPTIONS includes all expected workers."""
        worker_ids = [worker_id for _, worker_id in WORKER_OPTIONS]

        # Check for Unassigned
        assert None in worker_ids

        # Check for Alleycat workers
        assert "alleycat-1" in worker_ids
        assert "alleycat-2" in worker_ids
        assert "alleycat-3" in worker_ids

        # Check for Executor workers
        assert "executor-1" in worker_ids
        assert "executor-2" in worker_ids
        assert "executor-3" in worker_ids

        # Check for Local workers
        assert "local-1" in worker_ids
        assert "local-2" in worker_ids
        assert "local-3" in worker_ids

        # Check for X-Wing workers
        assert "xwing-1" in worker_ids
        assert "xwing-2" in worker_ids
        assert "xwing-3" in worker_ids


class TestGetWorkerDisplayName:
    """Tests for get_worker_display_name function."""

    def test_alleycat_workers(self):
        """Test correct mapping for Alleycat workers."""
        assert get_worker_display_name("alleycat-1") == "Alleycat 1"
        assert get_worker_display_name("alleycat-2") == "Alleycat 2"
        assert get_worker_display_name("alleycat-3") == "Alleycat 3"

    def test_executor_workers(self):
        """Test correct mapping for Executor workers."""
        assert get_worker_display_name("executor-1") == "Executor 1"
        assert get_worker_display_name("executor-2") == "Executor 2"
        assert get_worker_display_name("executor-3") == "Executor 3"

    def test_local_workers(self):
        """Test correct mapping for Local workers."""
        assert get_worker_display_name("local-1") == "Local 1"
        assert get_worker_display_name("local-2") == "Local 2"
        assert get_worker_display_name("local-3") == "Local 3"

    def test_xwing_workers(self):
        """Test correct mapping for X-Wing workers."""
        assert get_worker_display_name("xwing-1") == "X-Wing 1"
        assert get_worker_display_name("xwing-2") == "X-Wing 2"
        assert get_worker_display_name("xwing-3") == "X-Wing 3"

    def test_none_input(self):
        """Test behavior for None input (unassigned)."""
        assert get_worker_display_name(None) == ""

    def test_unknown_worker_id(self):
        """Test behavior for unknown/invalid worker IDs."""
        assert get_worker_display_name("unknown-worker") == ""
        assert get_worker_display_name("invalid-1") == ""
        assert get_worker_display_name("") == ""

    def test_case_sensitivity(self):
        """Test that worker IDs are case-sensitive."""
        # Should not match uppercase variants
        assert get_worker_display_name("ALLEYCAT-1") == ""
        assert get_worker_display_name("Alleycat-1") == ""
