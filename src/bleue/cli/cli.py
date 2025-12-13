"""Bleue CLI - TUI-first workflow management CLI."""

from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

from bleue import __version__


def _find_dotenv() -> Path | None:
    """Find .env file by searching up from current directory."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        env_file = parent / ".env"
        if env_file.is_file():
            return env_file
    return None


# Load environment variables from .env file (search up from cwd)
env_path = _find_dotenv()
load_dotenv(dotenv_path=env_path)

app = typer.Typer(
    invoke_without_command=True,
    no_args_is_help=False,
    help="Bleue CLI - TUI-first workflow management",
)


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"Bleue CLI version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Main entry point. Launches TUI if no subcommand provided."""
    if ctx.invoked_subcommand is None:
        # Import TUI here to avoid import errors if textual isn't installed
        try:
            from bleue.tui.app import BleuApp

            tui_app = BleuApp()
            tui_app.run()
        except ImportError as e:
            typer.echo(f"Error: TUI dependencies not available: {e}", err=True)
            typer.echo("Please install with: uv pip install bleue", err=True)
            raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Error launching TUI: {e}", err=True)
            raise typer.Exit(1)


if __name__ == "__main__":
    app()
