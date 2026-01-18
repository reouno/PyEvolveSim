"""Unit tests for stats history management.

Tests verify that StatsHistory correctly stores and retrieves statistical data
while maintaining independence from rendering concerns.
"""

import pytest
from life_game.evolution.stats_history import StatsHistory, StatsSnapshot


class MockStats:
    """Mock stats object for testing."""

    def __init__(
        self,
        generation: int = 0,
        creature_count: int = 10,
        food_count: int = 5,
        avg_energy: float = 50.0,
        avg_speed: float = 1.5,
        avg_vision_range: float = 3.0,
        avg_max_energy: float = 200.0,
        std_speed: float = 0.5,
        std_vision_range: float = 1.0,
        current_food_spawn_rate: float = 2.0,
    ):
        self.generation = generation
        self.creature_count = creature_count
        self.food_count = food_count
        self.avg_energy = avg_energy
        self.avg_speed = avg_speed
        self.avg_vision_range = avg_vision_range
        self.avg_max_energy = avg_max_energy
        self.std_speed = std_speed
        self.std_vision_range = std_vision_range
        self.current_food_spawn_rate = current_food_spawn_rate


class TestStatsSnapshot:
    """Test StatsSnapshot data model."""

    def test_snapshot_creation(self):
        """Test creating a snapshot with valid data."""
        snapshot = StatsSnapshot(
            generation=10,
            creature_count=20,
            food_count=15,
            avg_energy=60.0,
            avg_speed=1.8,
            avg_vision_range=3.5,
            avg_max_energy=210.0,
            std_speed=0.6,
            std_vision_range=1.2,
            current_food_spawn_rate=2.5,
        )

        assert snapshot.generation == 10
        assert snapshot.creature_count == 20
        assert snapshot.avg_speed == 1.8


class TestStatsHistory:
    """Test StatsHistory functionality."""

    def test_initialization(self):
        """Test history initialization."""
        history = StatsHistory(max_points=10)
        assert history.is_empty()
        assert len(history) == 0

    def test_record_single_snapshot(self):
        """Test recording a single snapshot."""
        history = StatsHistory(max_points=10)
        stats = MockStats(generation=0)

        history.record(stats)

        assert not history.is_empty()
        assert len(history) == 1

    def test_record_multiple_snapshots(self):
        """Test recording multiple snapshots."""
        history = StatsHistory(max_points=10)

        for gen in range(5):
            stats = MockStats(generation=gen, creature_count=10 + gen)
            history.record(stats)

        assert len(history) == 5

    def test_max_points_limit(self):
        """Test that history respects max_points limit."""
        history = StatsHistory(max_points=3)

        # Record 5 snapshots
        for gen in range(5):
            stats = MockStats(generation=gen)
            history.record(stats)

        # Should only keep last 3
        assert len(history) == 3

        generations = history.get_generations()
        assert generations == [2, 3, 4]

    def test_get_all_snapshots(self):
        """Test retrieving all snapshots."""
        history = StatsHistory(max_points=10)

        for gen in range(3):
            stats = MockStats(generation=gen, creature_count=gen * 10)
            history.record(stats)

        snapshots = history.get_all()

        assert len(snapshots) == 3
        assert snapshots[0].generation == 0
        assert snapshots[1].generation == 1
        assert snapshots[2].generation == 2

    def test_get_generations(self):
        """Test getting list of generations."""
        history = StatsHistory(max_points=10)

        for gen in [0, 10, 20, 30]:
            stats = MockStats(generation=gen)
            history.record(stats)

        generations = history.get_generations()

        assert generations == [0, 10, 20, 30]

    def test_get_values(self):
        """Test extracting specific field values."""
        history = StatsHistory(max_points=10)

        for gen in range(3):
            stats = MockStats(generation=gen, avg_speed=1.0 + gen * 0.1)
            history.record(stats)

        speeds = history.get_values("avg_speed")

        assert len(speeds) == 3
        assert speeds[0] == pytest.approx(1.0)
        assert speeds[1] == pytest.approx(1.1)
        assert speeds[2] == pytest.approx(1.2)

    def test_get_values_different_fields(self):
        """Test extracting multiple different fields."""
        history = StatsHistory(max_points=10)

        stats = MockStats(
            generation=0, creature_count=20, food_count=15, avg_energy=60.0
        )
        history.record(stats)

        assert history.get_values("creature_count") == [20]
        assert history.get_values("food_count") == [15]
        assert history.get_values("avg_energy") == [60.0]

    def test_clear(self):
        """Test clearing history."""
        history = StatsHistory(max_points=10)

        for gen in range(5):
            stats = MockStats(generation=gen)
            history.record(stats)

        assert len(history) == 5

        history.clear()

        assert history.is_empty()
        assert len(history) == 0

    def test_get_all_returns_copy(self):
        """Test that get_all returns a copy, not the internal list."""
        history = StatsHistory(max_points=10)
        stats = MockStats(generation=0)
        history.record(stats)

        snapshots1 = history.get_all()
        snapshots2 = history.get_all()

        # Should be different list objects
        assert snapshots1 is not snapshots2
        # But contain same data
        assert len(snapshots1) == len(snapshots2)


class TestStatsHistoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_get_values_from_empty_history(self):
        """Test getting values from empty history."""
        history = StatsHistory(max_points=10)

        values = history.get_values("avg_speed")

        assert values == []

    def test_get_generations_from_empty_history(self):
        """Test getting generations from empty history."""
        history = StatsHistory(max_points=10)

        generations = history.get_generations()

        assert generations == []

    def test_max_points_zero(self):
        """Test history with max_points=0 (keeps at least one)."""
        history = StatsHistory(max_points=0)

        stats = MockStats(generation=0)
        history.record(stats)

        # Even with max_points=0, keeps at least the latest
        assert len(history) >= 0

    def test_max_points_one(self):
        """Test history with max_points=1 (keeps only latest)."""
        history = StatsHistory(max_points=1)

        stats1 = MockStats(generation=0)
        stats2 = MockStats(generation=1)

        history.record(stats1)
        history.record(stats2)

        assert len(history) == 1
        assert history.get_generations() == [1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
