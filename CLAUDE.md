# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project called "life-game" managed with [uv](https://github.com/astral-sh/uv), a fast Python package manager. The project requires Python 3.13+.

## Development Commands

### Running the Application
```bash
uv run python main.py
```

### Type Checking and Code Quality

Run type checking with mypy:
```bash
uv run mypy main.py
```

Check code with ruff:
```bash
uv run ruff check .
```

Format code with ruff:
```bash
uv run ruff format .
```

Auto-fix issues with ruff:
```bash
uv run ruff check --fix .
```

### Managing Dependencies

Install/sync dependencies:
```bash
uv sync
```

Add a new dependency:
```bash
uv add <package-name>
```

Add a development dependency:
```bash
uv add --dev <package-name>
```

### Python Environment

The project uses Python 3.13 (specified in `.python-version`). The virtual environment is managed automatically by uv in `.venv/`.

## Code Architecture

The project currently has a minimal structure:
- `main.py`: Entry point with a main() function

No additional architectural patterns or conventions are established yet.
