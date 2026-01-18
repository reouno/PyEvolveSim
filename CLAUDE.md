# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project called "PyEvolveSim" managed with [uv](https://github.com/astral-sh/uv), a fast Python package manager. The project requires Python 3.13+.

## Development Commands

### Running the Application
```bash
uv run python main.py
```

### Type Checking and Code Quality

Run type checking with mypy:
```bash
uv run mypy main.py
uv run mypy pyevolvesim/evolution/  # Check evolution module
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

### Testing

Run all tests (71 tests total):
```bash
uv run pytest tests/ -v
```

Run specific test file:
```bash
uv run pytest tests/test_mutation.py -v           # Mutation logic (17 tests)
uv run pytest tests/test_creature_mutation.py -v  # Creature mutation (7 tests)
uv run pytest tests/test_evolution_features.py -v # Evolution features (12 tests)
uv run pytest tests/test_stats_history.py -v      # Stats history (15 tests)
uv run pytest tests/test_graph_renderer.py -v     # Graph rendering (20 tests)
```

Run tests with coverage:
```bash
uv run pytest tests/ --cov=life_game/evolution --cov-report=term-missing
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

### Project Structure

```
pyevolvesim/
├── evolution/          # Evolution simulation module
│   ├── behaviors.py       # Creature behavior logic (pure functions)
│   ├── config.py          # Configuration parameters
│   ├── creature.py        # Creature and Genes models
│   ├── food.py            # Food model
│   ├── graph_renderer.py  # Graph rendering (independent)
│   ├── mutation.py        # Mutation logic (pure functions, testable)
│   ├── renderer.py        # Terminal rendering
│   ├── simulation.py      # Simulation runner
│   ├── stats.py           # Statistics calculation
│   ├── stats_history.py   # Statistics history management (independent)
│   └── world.py           # World state management
├── game.py             # Conway's Game of Life
└── patterns.py         # Pattern definitions

tests/
├── test_mutation.py            # Unit tests for mutation logic (17 tests)
├── test_creature_mutation.py   # Integration tests for creature mutation (7 tests)
├── test_evolution_features.py  # Integration tests for evolution features (12 tests)
├── test_stats_history.py       # Unit tests for stats history (15 tests)
└── test_graph_renderer.py      # Unit tests for graph rendering (20 tests)

main.py                 # Entry point
```

### Design Principles

1. **Separation of Concerns**: Logic is separated into focused modules
   - `mutation.py`: Pure functions for gene mutation (easily testable)
   - `behaviors.py`: Pure functions for creature decisions
   - `world.py`: Immutable world state transitions
   - `stats_history.py`: Data collection (independent of rendering)
   - `graph_renderer.py`: Visualization (independent of data collection)

2. **Loose Coupling**: Components communicate through clear interfaces
   - `WorldStatsProvider` Protocol: Stats source interface
   - `StatsSnapshotProtocol` Protocol: Graph data interface
   - Graph functionality is optional and doesn't affect simulation

3. **Type Safety**: Full type hints with mypy validation
   - `GENE_CONSTRAINTS`: Type-safe gene range definitions
   - Pydantic models for data validation
   - Protocol types for interface definitions

4. **Testability**: Critical logic is unit tested (71 tests total)
   - Pure functions are separated for easy testing
   - Each module has dedicated unit tests
   - Integration tests verify system behavior

5. **Immutability**: State changes return new instances
   - Creatures and World use Pydantic's `model_copy()`
   - Functional approach prevents accidental state mutation
