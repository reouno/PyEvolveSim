"""Integration tests to verify evolution features are working correctly.

These tests verify the major features of the evolution system:
- Food clustering (Phase 1.1)
- Temporal variation (Phase 1.2)
- New genes: max_energy, food_efficiency (Phase 2.1, 2.2)
- Diversity metrics (Phase 4)
- Full simulation runs without errors
"""

import random
from pyevolvesim.evolution.world import EvolutionWorld
from pyevolvesim.evolution.creature import Creature, Genes
from pyevolvesim.evolution.stats import WorldStats
from pyevolvesim.evolution.config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    INITIAL_ENERGY,
    NUM_FOOD_CLUSTERS,
)


class TestFoodClustering:
    """Test Phase 1.1: Food Clustering."""

    def test_clusters_are_initialized(self):
        """Test that food clusters are created."""
        world = EvolutionWorld(
            width=WORLD_WIDTH,
            height=WORLD_HEIGHT,
            creatures=[],
            foods=[],
        )

        world.initialize_food_clusters()

        assert len(world.food_clusters) == NUM_FOOD_CLUSTERS
        # Each cluster should be a valid coordinate
        for cluster_x, cluster_y in world.food_clusters:
            assert 0 <= cluster_x < WORLD_WIDTH
            assert 0 <= cluster_y < WORLD_HEIGHT

    def test_food_spawns_near_clusters(self):
        """Test that food spawns near cluster centers."""
        world = EvolutionWorld(
            width=WORLD_WIDTH,
            height=WORLD_HEIGHT,
            creatures=[],
            foods=[],
        )

        world.initialize_food_clusters()

        # Spawn multiple food items
        occupied: set[tuple[int, int]] = set()
        food_positions: set[tuple[int, int]] = set()
        for _ in range(10):
            food = world.spawn_food_near_cluster(occupied, food_positions)
            if food:
                food_positions.add((food.x, food.y))

        # Should successfully spawn food
        assert len(food_positions) > 0


class TestTemporalVariation:
    """Test Phase 1.2: Temporal Variation."""

    def test_spawn_rate_varies_over_time(self):
        """Test that food spawn rate changes with generation."""
        world = EvolutionWorld(
            width=WORLD_WIDTH,
            height=WORLD_HEIGHT,
            creatures=[],
            foods=[],
            generation=0,
        )

        # Check spawn rate at different generations
        rate_gen_0 = world.get_food_spawn_rate()
        world.generation = 25
        rate_gen_25 = world.get_food_spawn_rate()
        world.generation = 50
        rate_gen_50 = world.get_food_spawn_rate()

        # Rates should vary (not all the same)
        rates = [rate_gen_0, rate_gen_25, rate_gen_50]
        assert len(set(rates)) > 1, "Spawn rate should vary over time"

    def test_spawn_rate_within_bounds(self):
        """Test that spawn rate stays within configured min/max."""
        from pyevolvesim.evolution.config import (
            SEASON_MIN_SPAWN_RATE,
            SEASON_MAX_SPAWN_RATE,
        )

        world = EvolutionWorld(
            width=WORLD_WIDTH,
            height=WORLD_HEIGHT,
            creatures=[],
            foods=[],
        )

        # Test across many generations
        for gen in range(100):
            world.generation = gen
            rate = world.get_food_spawn_rate()
            assert SEASON_MIN_SPAWN_RATE <= rate <= SEASON_MAX_SPAWN_RATE


class TestNewGenes:
    """Test Phase 2.1 & 2.2: New Genes (max_energy, food_efficiency)."""

    def test_max_energy_gene_exists(self):
        """Test that max_energy gene is present."""
        genes = Genes()
        creature = Creature(
            x=10,
            y=10,
            energy=INITIAL_ENERGY,
            genes=genes,
            id=0,
        )

        assert hasattr(creature.genes, "max_energy")
        assert 100.0 <= creature.genes.max_energy <= 300.0

    def test_food_efficiency_gene_exists(self):
        """Test that food_efficiency gene is present."""
        genes = Genes()
        creature = Creature(
            x=10,
            y=10,
            energy=INITIAL_ENERGY,
            genes=genes,
            id=0,
        )

        assert hasattr(creature.genes, "food_efficiency")
        assert 0.7 <= creature.genes.food_efficiency <= 1.3

    def test_energy_capped_at_max_energy(self):
        """Test that energy is capped at max_energy when eating."""
        creature = Creature(
            x=10,
            y=10,
            energy=INITIAL_ENERGY,
            genes=Genes(),
            id=0,
        )

        # Try to eat a huge amount
        creature_full = creature.eat(1000)

        # Energy should be capped at max_energy
        assert creature_full.energy <= creature.genes.max_energy

    def test_food_efficiency_affects_energy_gain(self):
        """Test that food_efficiency multiplies energy gained from food."""
        creature = Creature(
            x=10,
            y=10,
            energy=INITIAL_ENERGY,
            genes=Genes(),
            id=0,
        )

        initial_energy = creature.energy
        food_energy = 50.0

        creature_after_eating = creature.eat(food_energy)

        # Calculate expected energy gain
        expected_energy = min(
            initial_energy + food_energy * creature.genes.food_efficiency,
            creature.genes.max_energy,
        )

        # Should match (within floating point tolerance)
        assert abs(creature_after_eating.energy - expected_energy) < 0.01


class TestDiversityMetrics:
    """Test Phase 4: Diversity Metrics."""

    def test_diversity_metrics_exist(self):
        """Test that diversity metrics are calculated."""
        # Create creatures with varying genes
        creatures = []
        for i in range(10):
            genes = Genes(
                speed=1 + (i % 3),  # Vary speed 1-3
                vision_range=3 + (i % 5),  # Vary vision 3-7
                max_energy=150.0 + i * 10,  # Vary max_energy
            )
            creatures.append(
                Creature(
                    x=random.randint(0, WORLD_WIDTH - 1),
                    y=random.randint(0, WORLD_HEIGHT - 1),
                    energy=INITIAL_ENERGY,
                    genes=genes,
                    id=i,
                )
            )

        world = EvolutionWorld(
            width=WORLD_WIDTH,
            height=WORLD_HEIGHT,
            creatures=creatures,
            foods=[],
        )

        stats = WorldStats.from_world(world)

        # Check diversity metrics exist
        assert hasattr(stats, "std_speed")
        assert hasattr(stats, "std_vision_range")
        assert hasattr(stats, "std_max_energy")

    def test_diversity_metrics_are_nonzero(self):
        """Test that diversity metrics are non-zero when there is diversity."""
        # Create creatures with varying genes
        creatures = []
        for i in range(10):
            genes = Genes(
                speed=1 + (i % 3),  # Vary speed 1-3
                vision_range=3 + (i % 5),  # Vary vision 3-7
                max_energy=150.0 + i * 10,  # Vary max_energy
            )
            creatures.append(
                Creature(
                    x=random.randint(0, WORLD_WIDTH - 1),
                    y=random.randint(0, WORLD_HEIGHT - 1),
                    energy=INITIAL_ENERGY,
                    genes=genes,
                    id=i,
                )
            )

        world = EvolutionWorld(
            width=WORLD_WIDTH,
            height=WORLD_HEIGHT,
            creatures=creatures,
            foods=[],
        )

        stats = WorldStats.from_world(world)

        # With varied genes, diversity should be non-zero
        assert stats.std_speed > 0
        assert stats.std_vision_range > 0
        assert stats.std_max_energy > 0


class TestFullSimulation:
    """Test that full simulation runs without errors."""

    def test_simulation_runs_multiple_generations(self):
        """Test that simulation can run for multiple generations."""
        # Create initial creatures
        creatures = []
        for i in range(5):
            creatures.append(
                Creature(
                    x=random.randint(0, WORLD_WIDTH - 1),
                    y=random.randint(0, WORLD_HEIGHT - 1),
                    energy=INITIAL_ENERGY,
                    genes=Genes(),
                    id=i,
                )
            )

        world = EvolutionWorld(
            width=WORLD_WIDTH,
            height=WORLD_HEIGHT,
            creatures=creatures,
            foods=[],
        )

        # Initialize clusters
        world.initialize_food_clusters()

        # Run for 10 generations - should not crash
        for _ in range(10):
            world = world.next_step()

        # Verify simulation ran
        assert world.generation == 10

    def test_simulation_maintains_valid_state(self):
        """Test that simulation maintains valid world state."""
        # Create initial creatures
        creatures = []
        for i in range(5):
            creatures.append(
                Creature(
                    x=random.randint(0, WORLD_WIDTH - 1),
                    y=random.randint(0, WORLD_HEIGHT - 1),
                    energy=INITIAL_ENERGY,
                    genes=Genes(),
                    id=i,
                )
            )

        world = EvolutionWorld(
            width=WORLD_WIDTH,
            height=WORLD_HEIGHT,
            creatures=creatures,
            foods=[],
        )

        world.initialize_food_clusters()

        # Run for 20 generations
        for _ in range(20):
            world = world.next_step()

            # Verify all creatures have valid genes
            for creature in world.creatures:
                assert 100.0 <= creature.genes.max_energy <= 300.0
                assert 0.7 <= creature.genes.food_efficiency <= 1.3
                assert 1 <= creature.genes.speed <= 3
                assert 1 <= creature.genes.vision_range <= 10

            # Verify all positions are valid
            for creature in world.creatures:
                assert 0 <= creature.x < WORLD_WIDTH
                assert 0 <= creature.y < WORLD_HEIGHT

            for food in world.foods:
                assert 0 <= food.x < WORLD_WIDTH
                assert 0 <= food.y < WORLD_HEIGHT
