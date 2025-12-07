"""Tests for CLI commands."""

from typer.testing import CliRunner

from bleue.cli.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Bleue CLI" in result.output


def test_cli_version():
    """Test version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_removed_create_command():
    """Test that removed create command returns error."""
    result = runner.invoke(app, ["create", "Test issue"])
    assert result.exit_code != 0


def test_removed_create_from_file_command():
    """Test that removed create-from-file command returns error."""
    result = runner.invoke(app, ["create-from-file", "test.txt"])
    assert result.exit_code != 0


def test_removed_run_command():
    """Test that removed run command returns error."""
    result = runner.invoke(app, ["run", "123"])
    assert result.exit_code != 0
