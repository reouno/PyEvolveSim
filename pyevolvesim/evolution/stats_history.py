"""Statistics history management for evolution simulation.

This module manages the historical data of simulation statistics,
providing a clear interface for data collection and retrieval.
Designed to be independent of rendering concerns.
"""

from typing import Protocol
from pydantic import BaseModel


class StatsSnapshot(BaseModel):
    """Snapshot of statistics at a specific generation.

    This is the core data structure that bridges simulation and visualization.
    Any stats you want to graph should be included here.
    """

    generation: int
    creature_count: int
    food_count: int
    avg_energy: float
    avg_speed: float
    avg_vision_range: float
    avg_max_energy: float
    std_speed: float
    std_vision_range: float
    current_food_spawn_rate: float


class WorldStatsProvider(Protocol):
    """Protocol defining what stats source must provide.

    This allows StatsHistory to work with any object that provides these attributes,
    maintaining loose coupling between modules.
    """

    generation: int
    creature_count: int
    food_count: int
    avg_energy: float
    avg_speed: float
    avg_vision_range: float
    avg_max_energy: float
    std_speed: float
    std_vision_range: float
    current_food_spawn_rate: float


class StatsHistory:
    """Manages historical statistics data.

    Responsibilities:
    - Store snapshots at specified intervals
    - Provide access to historical data
    - Maintain maximum history size

    Does NOT handle:
    - Rendering/visualization
    - Simulation logic
    - File I/O
    """

    def __init__(self, max_points: int = 50):
        """Initialize stats history.

        Args:
            max_points: Maximum number of snapshots to keep in memory
        """
        self._snapshots: list[StatsSnapshot] = []
        self._max_points = max_points

    def record(self, stats: WorldStatsProvider) -> None:
        """Record a snapshot of current stats.

        Args:
            stats: Object implementing WorldStatsProvider protocol
        """
        snapshot = StatsSnapshot(
            generation=stats.generation,
            creature_count=stats.creature_count,
            food_count=stats.food_count,
            avg_energy=stats.avg_energy,
            avg_speed=stats.avg_speed,
            avg_vision_range=stats.avg_vision_range,
            avg_max_energy=stats.avg_max_energy,
            std_speed=stats.std_speed,
            std_vision_range=stats.std_vision_range,
            current_food_spawn_rate=stats.current_food_spawn_rate,
        )

        self._snapshots.append(snapshot)

        # Keep only most recent max_points
        if len(self._snapshots) > self._max_points:
            self._snapshots = self._snapshots[-self._max_points :]

    def get_all(self) -> list[StatsSnapshot]:
        """Get all recorded snapshots.

        Returns:
            List of snapshots in chronological order
        """
        return self._snapshots.copy()

    def get_generations(self) -> list[int]:
        """Get list of all recorded generations.

        Returns:
            List of generation numbers
        """
        return [s.generation for s in self._snapshots]

    def get_values(self, field_name: str) -> list[float]:
        """Get time series values for a specific field.

        Args:
            field_name: Name of the field to extract

        Returns:
            List of values for the specified field

        Raises:
            AttributeError: If field_name doesn't exist in StatsSnapshot
        """
        return [getattr(s, field_name) for s in self._snapshots]

    def clear(self) -> None:
        """Clear all recorded history."""
        self._snapshots.clear()

    def __len__(self) -> int:
        """Return number of recorded snapshots."""
        return len(self._snapshots)

    def is_empty(self) -> bool:
        """Check if history is empty."""
        return len(self._snapshots) == 0
