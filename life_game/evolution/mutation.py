"""Mutation logic for genetic traits.

This module provides pure functions for mutating gene values while respecting
their valid ranges. Separated for testability and type safety.
"""

import random
from typing import TypedDict


class GeneConstraints(TypedDict):
    """Type-safe definition of gene value constraints."""

    min_value: float
    max_value: float
    is_integer: bool


# Gene constraints - single source of truth for valid ranges
GENE_CONSTRAINTS: dict[str, GeneConstraints] = {
    "move_cost": {"min_value": 0.5, "max_value": 2.0, "is_integer": False},
    "vision_range": {"min_value": 1, "max_value": 10, "is_integer": True},
    "reproduction_threshold": {
        "min_value": 10.0,
        "max_value": float("inf"),
        "is_integer": False,
    },
    "metabolism": {"min_value": 0.8, "max_value": 2.0, "is_integer": False},
    "speed": {"min_value": 1, "max_value": 3, "is_integer": True},
    "max_energy": {"min_value": 100.0, "max_value": 300.0, "is_integer": False},
    "food_efficiency": {"min_value": 0.7, "max_value": 1.3, "is_integer": False},
}


def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value to be within [min_val, max_val]."""
    return max(min_val, min(max_val, value))


def mutate_integer_gene(
    current_value: int,
    min_value: int,
    max_value: int,
    large_mutation_chance: float,
) -> int:
    """
    Mutate an integer gene value with discrete steps.

    Args:
        current_value: Current gene value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        large_mutation_chance: Probability of large mutation (±2 instead of ±1)

    Returns:
        Mutated value clamped to valid range
    """
    # Large mutations jump by 2, normal mutations jump by 1
    if random.random() < large_mutation_chance:
        change = random.choice([-2, 2])
    else:
        change = random.choice([-1, 1])

    new_value = current_value + change
    return int(clamp_value(float(new_value), float(min_value), float(max_value)))


def mutate_continuous_gene(
    current_value: float,
    min_value: float,
    max_value: float,
    mutation_strength: float,
    large_mutation_strength: float,
    large_mutation_chance: float,
) -> float:
    """
    Mutate a continuous gene value with multiplicative factor.

    Args:
        current_value: Current gene value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        mutation_strength: Normal mutation strength (±%)
        large_mutation_strength: Large mutation strength (±%)
        large_mutation_chance: Probability of large mutation

    Returns:
        Mutated value clamped to valid range
    """
    # Choose mutation strength
    if random.random() < large_mutation_chance:
        strength = large_mutation_strength
    else:
        strength = mutation_strength

    # Apply multiplicative mutation
    mutation_factor = 1.0 + random.uniform(-strength, strength)
    new_value = current_value * mutation_factor

    # Clamp to valid range
    return clamp_value(new_value, min_value, max_value)


def mutate_gene_value(
    field_name: str,
    current_value: float | int,
    mutation_rate: float,
    mutation_strength: float,
    large_mutation_strength: float,
    large_mutation_chance: float,
) -> float | int:
    """
    Mutate a single gene value based on its constraints.

    Args:
        field_name: Name of the gene field
        current_value: Current value
        mutation_rate: Probability of mutation occurring
        mutation_strength: Normal mutation strength
        large_mutation_strength: Large mutation strength
        large_mutation_chance: Probability of large mutation

    Returns:
        Mutated value (or original if no mutation) clamped to valid range
    """
    # Check if mutation occurs
    if random.random() >= mutation_rate:
        return current_value

    # Get constraints for this gene
    if field_name not in GENE_CONSTRAINTS:
        # Unknown gene, return unchanged
        return current_value

    constraints = GENE_CONSTRAINTS[field_name]

    # Apply appropriate mutation based on type
    if constraints["is_integer"]:
        return mutate_integer_gene(
            int(current_value),
            int(constraints["min_value"]),
            int(constraints["max_value"]),
            large_mutation_chance,
        )
    else:
        return mutate_continuous_gene(
            float(current_value),
            constraints["min_value"],
            constraints["max_value"],
            mutation_strength,
            large_mutation_strength,
            large_mutation_chance,
        )
