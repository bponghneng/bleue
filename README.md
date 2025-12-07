# CAPE TUI

## Overview

The `cape` package provides a Textual-based terminal user interface (TUI) for
CAPE workflow management. It provides an interactive interface for browsing
issues, viewing details, and managing workflow status using Supabase for
persistence.

## Quick Start

```bash
cd cape/app
uv sync

# Launch the interactive TUI
uv run cape

# Show version
uv run cape --version
```

## Environment & Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `SUPABASE_URL` | Yes | Supabase project URL. |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Service role key used by the TUI. |

Create a `.env` or set the variables in your shell before running.

## TUI Features

- **Issue List View** - Browse the Supabase backlog with ID, description,
  status, and created timestamp.
- **Issue Detail** - View metadata and comments with auto-refresh timer that
  keeps "started" issues up to date.
- **Keyboard shortcuts** - `n` (new issue), `Enter`/`v` (details), `d` (delete
  pending issue), `q` (quit), `?` (help), `Ctrl+S` (save forms), `Esc` (close
  modal).

## Tests

```bash
cd cape/app
uv run pytest tests/ -v
```

## Project Layout

```
bleue/
├── pyproject.toml        # build configuration
├── src/cape/
│   ├── cli/              # Typer CLI entry point
│   ├── core/             # Shared infrastructure (database, models, utils)
│   └── tui/              # Textual TUI components and screens
└── tests/                # unit tests
```
