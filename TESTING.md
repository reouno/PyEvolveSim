# Testing Guide

## Overview

This project has comprehensive test coverage with 36 tests organized in three test suites:

```
tests/
├── test_mutation.py            # Unit tests for mutation logic (17 tests)
├── test_creature_mutation.py   # Integration tests for creature mutation (7 tests)
└── test_evolution_features.py  # Integration tests for evolution features (12 tests)
```

## Running Tests

### Run All Tests

```bash
uv run pytest tests/ -v
```

Output:
```
36 passed in 0.12s
```

### Run Specific Test Suite

```bash
# Mutation logic tests
uv run pytest tests/test_mutation.py -v

# Creature mutation integration tests
uv run pytest tests/test_creature_mutation.py -v

# Evolution features integration tests
uv run pytest tests/test_evolution_features.py -v
```

### Run Tests with Coverage

```bash
# Install coverage tool
uv add --dev pytest-cov

# Run with coverage report
uv run pytest tests/ --cov=life_game/evolution --cov-report=term-missing
```

### Run Specific Test

```bash
# By test name
uv run pytest tests/test_mutation.py::TestClampValue::test_clamp_within_range -v

# By keyword
uv run pytest tests/ -k "regression" -v
```

## Test Suites

### 1. Mutation Logic Tests (`test_mutation.py`)

**Purpose**: Test pure mutation functions in isolation

**17 tests covering**:
- Value clamping (3 tests)
- Integer gene mutations (3 tests)
- Continuous gene mutations (3 tests)
- Gene value mutation (3 tests)
- Gene constraints validation (3 tests)
- Edge cases (2 tests)

**Key test cases**:
```python
def test_mutation_stays_in_range():
    """Test 100 random mutations stay within bounds."""
    for _ in range(100):
        result = mutate_continuous_gene(...)
        assert 100.0 <= result <= 300.0

def test_tight_range_mutation():
    """Test mutations in tight ranges (0.7-1.3)."""
    for _ in range(100):
        result = mutate_continuous_gene(...)
        assert 0.7 <= result <= 1.3
```

### 2. Creature Mutation Tests (`test_creature_mutation.py`)

**Purpose**: Test mutation integration with Creature/Genes models

**7 tests covering**:
- Genes mutation never exceeds field constraints (1 test)
- Regression tests for reported bugs (2 tests)
- Multi-generation mutation chains (1 test)
- Creature reproduction with mutation (2 tests)
- Reproduction chains (1 test)

**Key test cases**:
```python
def test_regression_max_energy_overflow():
    """Regression: max_energy should not exceed 300."""
    genes = Genes(max_energy=290.0)
    for _ in range(200):
        mutated = genes.mutate()
        assert mutated.max_energy <= 300.0

def test_reproduction_chain_maintains_validity():
    """Test 20 generations of reproduction."""
    for generation in range(20):
        parent_after, child = creature.reproduce(generation)
        assert 100.0 <= child.genes.max_energy <= 300.0
```

### 3. Evolution Features Tests (`test_evolution_features.py`)

**Purpose**: Test high-level evolution system features

**12 tests covering**:
- Food clustering (2 tests)
- Temporal variation (2 tests)
- New genes: max_energy, food_efficiency (4 tests)
- Diversity metrics (2 tests)
- Full simulation runs (2 tests)

**Key test cases**:
```python
def test_spawn_rate_varies_over_time():
    """Test food spawn rate changes with generation."""
    rates = [rate_gen_0, rate_gen_25, rate_gen_50]
    assert len(set(rates)) > 1

def test_simulation_maintains_valid_state():
    """Test 20 generations maintain valid state."""
    for _ in range(20):
        world = world.next_step()
        for creature in world.creatures:
            assert 100.0 <= creature.genes.max_energy <= 300.0
```

## Test Organization

### Class-Based Organization

Tests are organized into classes for better structure:

```python
class TestClampValue:
    """Test the clamp_value function."""

    def test_clamp_within_range(self):
        """Value within range should not change."""
        ...

    def test_clamp_below_min(self):
        """Value below min should be clamped to min."""
        ...
```

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names that explain what is being tested

### Fixtures (if needed)

```python
import pytest

@pytest.fixture
def sample_creature():
    """Create a sample creature for testing."""
    return Creature(
        x=10, y=10,
        energy=60.0,
        genes=Genes(),
        id=0
    )
```

## Continuous Integration

Add to GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: uv sync
      - name: Run type checks
        run: uv run mypy life_game/evolution/ tests/
      - name: Run linting
        run: uv run ruff check .
      - name: Run tests
        run: uv run pytest tests/ -v
```

## Test Coverage Goals

Target coverage: **80%+** for critical modules

Priority areas:
- ✅ Mutation logic (`mutation.py`) - **100%** (fully tested)
- ✅ Creature/Genes models (`creature.py`) - High coverage
- ⚠️ World state transitions (`world.py`) - Needs more tests
- ⚠️ Behavior logic (`behaviors.py`) - Could use more tests

## Writing New Tests

### 1. Unit Test Template

```python
class TestNewFeature:
    """Test the new feature."""

    def test_basic_functionality(self):
        """Test basic use case."""
        result = new_feature(input_value)
        assert result == expected_value

    def test_edge_case(self):
        """Test edge case behavior."""
        result = new_feature(edge_value)
        assert result is not None
```

### 2. Integration Test Template

```python
class TestNewIntegration:
    """Test new feature integration."""

    def test_integration_with_existing_system(self):
        """Test feature works with existing system."""
        world = EvolutionWorld(...)
        world = world.next_step()
        assert world.some_property == expected
```

### 3. Regression Test Template

```python
def test_regression_bug_fix():
    """Regression test for bug #123."""
    # Reproduce the bug scenario
    result = problematic_function(edge_case_input)
    # Verify the bug is fixed
    assert result <= max_allowed_value
```

## Debugging Failed Tests

### Run with verbose output

```bash
uv run pytest tests/ -vv
```

### Run with print statements visible

```bash
uv run pytest tests/ -s
```

### Run with debugger on failure

```bash
uv run pytest tests/ --pdb
```

### Show local variables on failure

```bash
uv run pytest tests/ -l
```

## Best Practices

1. **Test One Thing**: Each test should verify one specific behavior
2. **Use Descriptive Names**: Test names should explain what they test
3. **Arrange-Act-Assert**: Organize tests in three sections
4. **Test Edge Cases**: Don't just test the happy path
5. **Keep Tests Fast**: Unit tests should run in milliseconds
6. **Avoid Test Dependencies**: Tests should be independent
7. **Use Fixtures**: Share setup code with pytest fixtures

## Quick Reference

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific file
uv run pytest tests/test_mutation.py -v

# Run specific test
uv run pytest tests/test_mutation.py::TestClampValue::test_clamp_within_range -v

# Run tests matching keyword
uv run pytest tests/ -k "mutation" -v

# Run with coverage
uv run pytest tests/ --cov=life_game/evolution

# Run with output
uv run pytest tests/ -s

# Run with debugger
uv run pytest tests/ --pdb

# Show slowest tests
uv run pytest tests/ --durations=10
```
