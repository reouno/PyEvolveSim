"""Integration tests for Creature mutation.

These tests verify that the Genes.mutate() method correctly produces
valid gene values that respect Pydantic field constraints.
"""

import pytest
from pyevolvesim.evolution.creature import Genes, Creature


class TestGenesMutation:
    """Test Genes mutation integration."""

    def test_mutation_never_exceeds_bounds(self):
        """Mutated genes should never exceed field constraints."""
        # Create genes at various starting points
        test_cases = [
            # At boundaries
            Genes(
                max_energy=100.0,  # At minimum
                food_efficiency=0.7,  # At minimum
                speed=1,  # At minimum
                vision_range=1,  # At minimum
            ),
            Genes(
                max_energy=300.0,  # At maximum
                food_efficiency=1.3,  # At maximum
                speed=3,  # At maximum
                vision_range=10,  # At maximum
            ),
            # At middle
            Genes(
                max_energy=200.0,
                food_efficiency=1.0,
                speed=2,
                vision_range=5,
            ),
        ]

        # Test many mutations for each case
        for original_genes in test_cases:
            for _ in range(100):
                mutated = original_genes.mutate()

                # Check all fields are within bounds
                assert 0.1 <= mutated.move_cost, "move_cost below minimum"
                assert 1 <= mutated.vision_range <= 10, "vision_range out of bounds"
                assert 10.0 <= mutated.reproduction_threshold, (
                    "reproduction_threshold below minimum"
                )
                assert 0.1 <= mutated.metabolism, "metabolism below minimum"
                assert 1 <= mutated.speed <= 3, "speed out of bounds"
                assert 100.0 <= mutated.max_energy <= 300.0, "max_energy out of bounds"
                assert 0.7 <= mutated.food_efficiency <= 1.3, (
                    "food_efficiency out of bounds"
                )

    def test_regression_max_energy_overflow(self):
        """Regression test: max_energy should not exceed 300 after mutation."""
        # This was the bug reported: max_energy became 319.5
        genes = Genes(max_energy=290.0)  # Near maximum

        # Test many mutations - should never exceed 300
        for _ in range(200):
            mutated = genes.mutate()
            assert mutated.max_energy <= 300.0, (
                f"max_energy exceeded maximum: {mutated.max_energy}"
            )

    def test_regression_food_efficiency_overflow(self):
        """Regression test: food_efficiency should not exceed 1.3 after mutation."""
        # This was the bug reported: food_efficiency became 1.417
        genes = Genes(food_efficiency=1.25)  # Near maximum

        # Test many mutations - should never exceed 1.3
        for _ in range(200):
            mutated = genes.mutate()
            assert mutated.food_efficiency <= 1.3, (
                f"food_efficiency exceeded maximum: {mutated.food_efficiency}"
            )

    def test_mutation_returns_valid_genes_instance(self):
        """Mutation should return a valid Genes instance."""
        genes = Genes()

        for _ in range(50):
            mutated = genes.mutate()
            assert isinstance(mutated, Genes)
            # If we got here without ValidationError, Pydantic validated successfully

    def test_multiple_generation_mutations(self):
        """Test mutations across multiple generations stay valid."""
        genes = Genes()

        # Simulate 50 generations of mutations
        for generation in range(50):
            genes = genes.mutate()

            # Verify all constraints still hold
            assert 0.1 <= genes.move_cost
            assert 1 <= genes.vision_range <= 10
            assert 10.0 <= genes.reproduction_threshold
            assert 0.1 <= genes.metabolism
            assert 1 <= genes.speed <= 3
            assert 100.0 <= genes.max_energy <= 300.0
            assert 0.7 <= genes.food_efficiency <= 1.3


class TestCreatureReproduction:
    """Test that reproduction with mutation works correctly."""

    def test_child_has_valid_genes_after_reproduction(self):
        """Child creatures should have valid mutated genes."""
        creature = Creature(
            x=10,
            y=10,
            energy=150.0,
            genes=Genes(),
            id=0,
        )

        # Test many reproductions
        for child_id in range(100):
            parent_after, child = creature.reproduce(child_id)

            # Child should have valid genes
            assert isinstance(child.genes, Genes)
            assert 100.0 <= child.genes.max_energy <= 300.0
            assert 0.7 <= child.genes.food_efficiency <= 1.3
            assert 1 <= child.genes.speed <= 3
            assert 1 <= child.genes.vision_range <= 10

    def test_reproduction_chain_maintains_validity(self):
        """Test reproduction chain: parent → child → grandchild."""
        creature = Creature(
            x=10,
            y=10,
            energy=150.0,
            genes=Genes(),
            id=0,
        )

        # Simulate generational reproduction
        for generation in range(20):
            # Give creature enough energy to reproduce
            creature = creature.model_copy(update={"energy": 150.0})

            parent_after, child = creature.reproduce(generation + 1)

            # Child should have valid genes
            assert 100.0 <= child.genes.max_energy <= 300.0
            assert 0.7 <= child.genes.food_efficiency <= 1.3

            # Continue with child for next generation
            creature = child


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
