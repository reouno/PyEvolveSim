# Mutation Bug Fix & Code Improvements

## Problem

The simulation crashed with a Pydantic ValidationError after ~17 generations:

```
ValidationError: 2 validation errors for Genes
max_energy
  Input should be less than or equal to 300 [type=less_than_equal, input_value=319.5058755025897]
food_efficiency
  Input should be less than or equal to 1.3 [type=less_than_equal, input_value=1.417251296261961]
```

**Root Cause**: The mutation logic applied multiplicative factors (±25% or ±50%) without clamping the resulting values to their valid ranges. Over multiple generations, mutations could compound and exceed the field constraints.

## Solution

### 1. Separated Mutation Logic (`mutation.py`)

Created a dedicated module with pure functions for mutation:

```python
# Pure, testable functions
def clamp_value(value, min_val, max_val) -> float
def mutate_integer_gene(...) -> int
def mutate_continuous_gene(...) -> float
def mutate_gene_value(...) -> float | int
```

**Benefits**:
- **Pure functions**: No side effects, easy to test
- **Single responsibility**: Each function has one clear purpose
- **Type safe**: Explicit type hints and return types

### 2. Gene Constraints as Single Source of Truth

```python
GENE_CONSTRAINTS: dict[str, GeneConstraints] = {
    "max_energy": {"min_value": 100.0, "max_value": 300.0, "is_integer": False},
    "food_efficiency": {"min_value": 0.7, "max_value": 1.3, "is_integer": False},
    # ... other genes
}
```

**Benefits**:
- Centralized constraint definitions
- Type-safe with `TypedDict`
- Easy to maintain and extend
- Used by both mutation logic and tests

### 3. Clamping After Mutation

All mutations now clamp values to valid ranges:

```python
def mutate_continuous_gene(...) -> float:
    mutation_factor = 1.0 + random.uniform(-strength, strength)
    new_value = current_value * mutation_factor
    # Critical: clamp to valid range
    return clamp_value(new_value, min_value, max_value)
```

### 4. Simplified Genes.mutate()

```python
def mutate(self) -> "Genes":
    new_genes: dict[str, float | int] = {}
    for field_name, value in self.model_dump().items():
        new_value = mutate_gene_value(  # Uses mutation.py
            field_name=field_name,
            current_value=value,
            mutation_rate=MUTATION_RATE,
            # ... other params
        )
        new_genes[field_name] = new_value
    return Genes(**new_genes)  # type: ignore[arg-type]
```

**Benefits**:
- Simpler and more maintainable
- Delegates complex logic to tested functions
- Type annotation for mypy (with appropriate ignore)

## Testing

### Test Structure

All tests are organized in the `tests/` directory and can be run with pytest:

```bash
uv run pytest tests/ -v  # Run all 36 tests
```

#### Unit Tests (`tests/test_mutation.py`)

17 unit tests covering:
- `clamp_value()` edge cases
- Integer gene mutations (vision, speed)
- Continuous gene mutations (max_energy, food_efficiency)
- Boundary conditions
- Extreme mutation strengths
- Constraint definitions

**Key test cases**:
```python
def test_mutation_stays_in_range():
    """Test 100 random mutations stay within bounds."""
    for _ in range(100):
        result = mutate_continuous_gene(
            current_value=150.0,
            min_value=100.0,
            max_value=300.0,
            # ...
        )
        assert 100.0 <= result <= 300.0
```

#### Integration Tests (`tests/test_creature_mutation.py`)

7 integration tests covering:
- Genes mutation never exceeds bounds
- Regression tests for reported bugs
- Multi-generation mutation chains
- Creature reproduction with mutation

**Regression test**:
```python
def test_regression_max_energy_overflow():
    """Ensure max_energy never exceeds 300."""
    genes = Genes(max_energy=290.0)  # Near maximum
    for _ in range(200):
        mutated = genes.mutate()
        assert mutated.max_energy <= 300.0
```

#### Evolution Feature Tests (`tests/test_evolution_features.py`)

12 integration tests covering:
- Food clustering initialization and spawning
- Temporal variation in spawn rates
- New genes (max_energy, food_efficiency) functionality
- Diversity metrics calculation
- Full simulation runs without errors

### Test Results

All 36 tests pass:
```bash
$ uv run pytest tests/ -v
======================== 36 passed in 0.12s =========================
```

## Code Quality Improvements

### Type Safety

- Full mypy compliance (no errors)
- Type-safe gene constraints with `TypedDict`
- Explicit return types on all functions

### Separation of Concerns

| Module | Responsibility |
|--------|----------------|
| `mutation.py` | Pure mutation logic |
| `creature.py` | Creature/Genes models |
| `config.py` | Configuration |
| `tests/test_mutation.py` | Unit tests |
| `tests/test_creature_mutation.py` | Integration tests |

### Documentation

- Updated `CLAUDE.md` with:
  - Testing commands
  - Project structure
  - Design principles
- Created `MUTATION_FIX.md` (this document)
- Inline docstrings for all functions

## Verification

### 1. Type Checking
```bash
$ uv run mypy pyevolvesim/evolution/ tests/
Success: no issues found in 13 source files ✓
```

### 2. Linting
```bash
$ uv run ruff check .
All checks passed! ✓
```

### 3. All Tests
```bash
$ uv run pytest tests/ -v
36 passed in 0.12s ✓
```

### 4. Live Simulation
Ran simulation for 40+ generations without crashes:
```
Generation 41
Creatures: 58  |  Food: 6  |  Spawn Rate: 2.5
✓ No ValidationErrors
✓ All genes within bounds
```

## Summary

### What Was Fixed
- ✅ Mutation values now clamped to valid ranges
- ✅ No more ValidationErrors during reproduction
- ✅ Simulation runs indefinitely without crashes

### What Was Improved
- ✅ Separated mutation logic into pure functions
- ✅ Added comprehensive unit tests (17 tests)
- ✅ Added integration tests (19 tests)
- ✅ All tests runnable with single pytest command
- ✅ Type-safe gene constraints
- ✅ Better separation of concerns
- ✅ Improved documentation

### Design Benefits
- **Testability**: Pure functions easy to test
- **Type Safety**: Full mypy compliance
- **Maintainability**: Clear module boundaries
- **Reliability**: Comprehensive test coverage
