"""Unit tests for mutation logic.

These tests verify that mutation functions correctly handle gene values
while respecting their valid ranges.
"""

import pytest
from life_game.evolution.mutation import (
    clamp_value,
    mutate_integer_gene,
    mutate_continuous_gene,
    mutate_gene_value,
    GENE_CONSTRAINTS,
)


class TestClampValue:
    """Test the clamp_value function."""

    def test_clamp_within_range(self):
        """Value within range should not change."""
        assert clamp_value(5.0, 0.0, 10.0) == 5.0
        assert clamp_value(0.0, 0.0, 10.0) == 0.0
        assert clamp_value(10.0, 0.0, 10.0) == 10.0

    def test_clamp_below_min(self):
        """Value below min should be clamped to min."""
        assert clamp_value(-5.0, 0.0, 10.0) == 0.0
        assert clamp_value(0.5, 1.0, 10.0) == 1.0

    def test_clamp_above_max(self):
        """Value above max should be clamped to max."""
        assert clamp_value(15.0, 0.0, 10.0) == 10.0
        assert clamp_value(200.0, 0.0, 100.0) == 100.0


class TestMutateIntegerGene:
    """Test integer gene mutation."""

    def test_mutation_stays_in_range(self):
        """Mutated values should always stay within valid range."""
        # Test many mutations to ensure randomness doesn't break it
        for _ in range(100):
            result = mutate_integer_gene(
                current_value=5,
                min_value=1,
                max_value=10,
                large_mutation_chance=0.1,
            )
            assert 1 <= result <= 10
            assert isinstance(result, int)

    def test_mutation_at_boundaries(self):
        """Mutations at boundaries should not exceed limits."""
        # At minimum boundary
        for _ in range(50):
            result = mutate_integer_gene(
                current_value=1,
                min_value=1,
                max_value=10,
                large_mutation_chance=0.1,
            )
            assert result >= 1

        # At maximum boundary
        for _ in range(50):
            result = mutate_integer_gene(
                current_value=10,
                min_value=1,
                max_value=10,
                large_mutation_chance=0.1,
            )
            assert result <= 10

    def test_small_range_mutation(self):
        """Mutations in small ranges (like speed: 1-3) should work."""
        for _ in range(50):
            result = mutate_integer_gene(
                current_value=2,
                min_value=1,
                max_value=3,
                large_mutation_chance=0.0,  # No large mutations
            )
            assert 1 <= result <= 3
            assert isinstance(result, int)


class TestMutateContinuousGene:
    """Test continuous gene mutation."""

    def test_mutation_stays_in_range(self):
        """Mutated values should always stay within valid range."""
        for _ in range(100):
            result = mutate_continuous_gene(
                current_value=150.0,
                min_value=100.0,
                max_value=300.0,
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=0.1,
            )
            assert 100.0 <= result <= 300.0

    def test_mutation_at_boundaries(self):
        """Mutations at boundaries should be clamped."""
        # Near minimum with large mutation
        for _ in range(50):
            result = mutate_continuous_gene(
                current_value=100.5,
                min_value=100.0,
                max_value=300.0,
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=1.0,  # Always large mutation
            )
            assert result >= 100.0

        # Near maximum with large mutation
        for _ in range(50):
            result = mutate_continuous_gene(
                current_value=299.5,
                min_value=100.0,
                max_value=300.0,
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=1.0,  # Always large mutation
            )
            assert result <= 300.0

    def test_tight_range_mutation(self):
        """Mutations in tight ranges (like food_efficiency: 0.7-1.3) should work."""
        for _ in range(100):
            result = mutate_continuous_gene(
                current_value=1.0,
                min_value=0.7,
                max_value=1.3,
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=0.1,
            )
            assert 0.7 <= result <= 1.3


class TestMutateGeneValue:
    """Test the main mutation function."""

    def test_mutation_respects_gene_constraints(self):
        """Mutations should respect defined gene constraints."""
        # Test max_energy (100-300 range)
        for _ in range(100):
            result = mutate_gene_value(
                field_name="max_energy",
                current_value=200.0,
                mutation_rate=1.0,  # Always mutate
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=0.1,
            )
            assert 100.0 <= result <= 300.0

        # Test food_efficiency (0.7-1.3 range)
        for _ in range(100):
            result = mutate_gene_value(
                field_name="food_efficiency",
                current_value=1.0,
                mutation_rate=1.0,  # Always mutate
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=0.1,
            )
            assert 0.7 <= result <= 1.3

        # Test speed (1-3 range, integer)
        for _ in range(100):
            result = mutate_gene_value(
                field_name="speed",
                current_value=2,
                mutation_rate=1.0,  # Always mutate
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=0.1,
            )
            assert 1 <= result <= 3
            assert isinstance(result, int)

    def test_no_mutation_returns_original(self):
        """When mutation doesn't occur, original value should be returned."""
        result = mutate_gene_value(
            field_name="max_energy",
            current_value=200.0,
            mutation_rate=0.0,  # Never mutate
            mutation_strength=0.25,
            large_mutation_strength=0.5,
            large_mutation_chance=0.1,
        )
        assert result == 200.0

    def test_unknown_gene_returns_original(self):
        """Unknown gene names should return original value unchanged."""
        result = mutate_gene_value(
            field_name="unknown_gene",
            current_value=42.0,
            mutation_rate=1.0,  # Always try to mutate
            mutation_strength=0.25,
            large_mutation_strength=0.5,
            large_mutation_chance=0.1,
        )
        assert result == 42.0


class TestGeneConstraints:
    """Test that gene constraints are properly defined."""

    def test_all_genes_have_constraints(self):
        """All expected genes should have constraint definitions."""
        expected_genes = {
            "move_cost",
            "vision_range",
            "reproduction_threshold",
            "metabolism",
            "speed",
            "max_energy",
            "food_efficiency",
        }
        assert set(GENE_CONSTRAINTS.keys()) == expected_genes

    def test_constraints_have_required_fields(self):
        """Each constraint should have min, max, and is_integer fields."""
        for gene_name, constraints in GENE_CONSTRAINTS.items():
            assert "min_value" in constraints, f"{gene_name} missing min_value"
            assert "max_value" in constraints, f"{gene_name} missing max_value"
            assert "is_integer" in constraints, f"{gene_name} missing is_integer"

    def test_min_less_than_max(self):
        """Min values should be less than max values (where finite)."""
        for gene_name, constraints in GENE_CONSTRAINTS.items():
            min_val = constraints["min_value"]
            max_val = constraints["max_value"]
            if max_val != float("inf"):
                assert min_val < max_val, f"{gene_name} has min >= max"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_extreme_mutation_strength(self):
        """Test with extreme mutation strengths."""
        # Very high mutation strength should still respect bounds
        for _ in range(50):
            result = mutate_continuous_gene(
                current_value=200.0,
                min_value=100.0,
                max_value=300.0,
                mutation_strength=0.9,  # 90% variation
                large_mutation_strength=0.9,
                large_mutation_chance=0.5,
            )
            assert 100.0 <= result <= 300.0

    def test_value_at_exact_boundary(self):
        """Test mutation when value is exactly at boundary."""
        # At minimum
        for _ in range(50):
            result = mutate_continuous_gene(
                current_value=100.0,
                min_value=100.0,
                max_value=300.0,
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=0.1,
            )
            assert result >= 100.0

        # At maximum
        for _ in range(50):
            result = mutate_continuous_gene(
                current_value=300.0,
                min_value=100.0,
                max_value=300.0,
                mutation_strength=0.25,
                large_mutation_strength=0.5,
                large_mutation_chance=0.1,
            )
            assert result <= 300.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
