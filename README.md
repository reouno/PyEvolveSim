# PyEvolveSim

A Python-based evolution simulation featuring autonomous creatures with genetic traits, along with Conway's Game of Life implementation.

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)

## Installation

```bash
# Install dependencies
uv sync
```

## Usage

Run the simulation:

```bash
uv run python main.py
```

## Development

### Testing

```bash
# Run all tests (106 tests)
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=pyevolvesim/evolution --cov-report=term-missing
```

### Code Quality

```bash
# Type checking
uv run mypy main.py

# Linting and formatting
uv run ruff check .
uv run ruff format .
```

## Project Structure

- `pyevolvesim/evolution/` - Evolution simulation with genetic creatures
- `pyevolvesim/life_game/` - Conway's Game of Life implementation
- `main.py` - Entry point

## License

MIT
