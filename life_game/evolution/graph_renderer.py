"""Graph rendering for evolution simulation statistics.

This module handles visualization of statistical data in the terminal.
Designed to be independent of data collection concerns.
"""

from typing import Protocol


class StatsSnapshotProtocol(Protocol):
    """Protocol for stats snapshot data.

    This allows GraphRenderer to work with any object providing these attributes,
    maintaining loose coupling.
    """

    generation: int
    creature_count: int
    avg_speed: float
    std_speed: float


class GraphRenderer:
    """Renders statistics as ASCII graphs in the terminal.

    Responsibilities:
    - Render time-series data as ASCII graphs
    - Format graph labels and axes
    - Handle different graph heights and widths

    Does NOT handle:
    - Data collection
    - Data storage
    - Simulation logic
    """

    def __init__(self, height: int = 10, width: int = 50):
        """Initialize graph renderer.

        Args:
            height: Height of graph area in lines
            width: Width of graph area in characters
        """
        self.height = height
        self.width = width

    def render_sparkline(
        self,
        values: list[float],
        label: str,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> list[str]:
        """Render a sparkline graph (simple line using unicode characters).

        Args:
            values: List of values to plot
            label: Label for the graph
            min_val: Optional minimum value for scaling (auto-detected if None)
            max_val: Optional maximum value for scaling (auto-detected if None)

        Returns:
            List of strings representing the graph lines
        """
        if not values:
            return [f"{label}: (no data)"]

        # Determine value range
        data_min = min(values) if min_val is None else min_val
        data_max = max(values) if max_val is None else max_val

        # Avoid division by zero
        if data_max == data_min:
            data_max = data_min + 1.0

        # Sparkline characters (8 levels)
        chars = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

        # Normalize and convert to sparkline
        sparkline = []
        for value in values[-self.width :]:  # Take last width values
            normalized = (value - data_min) / (data_max - data_min)
            index = int(normalized * (len(chars) - 1))
            index = max(0, min(len(chars) - 1, index))
            sparkline.append(chars[index])

        # Format output
        latest = values[-1] if values else 0.0
        lines = [
            f"{label}: {latest:.2f}",
            "".join(sparkline),
            f"  {'─' * len(sparkline)}",
        ]

        return lines


class GraphDisplay:
    """High-level interface for displaying graphs.

    This class coordinates the rendering of multiple graphs
    and provides a simple interface for the simulation.
    """

    def __init__(self, renderer: GraphRenderer, separator_width: int = 52):
        """Initialize graph display.

        Args:
            renderer: GraphRenderer instance to use
            separator_width: Width of separator lines (defaults to 52)
        """
        self.renderer = renderer
        self.separator_width = separator_width

    def render_evolution_graphs(
        self,
        generations: list[int],
        creature_counts: list[float],
        avg_speeds: list[float],
        std_speeds: list[float],
    ) -> str:
        """Render evolution statistics graphs.

        Args:
            generations: List of generation numbers
            creature_counts: List of creature counts
            avg_speeds: List of average speeds
            std_speeds: List of speed diversity values

        Returns:
            Formatted string with all graphs
        """
        lines = []

        # Title (compact header)
        lines.append("=" * self.separator_width)
        lines.append("Evolution Statistics")
        lines.append("=" * self.separator_width)

        if not generations:
            lines.append("(Collecting data...)")
            return "\n".join(lines)

        # Population graph
        lines.extend(
            self.renderer.render_sparkline(creature_counts, "Population", min_val=0)
        )

        # Average speed graph
        lines.extend(
            self.renderer.render_sparkline(
                avg_speeds, "Avg Speed", min_val=1.0, max_val=3.0
            )
        )

        # Speed diversity graph
        lines.extend(
            self.renderer.render_sparkline(std_speeds, "Speed Diversity (σ)", min_val=0)
        )

        # Generation range
        lines.append(f"Showing generations {generations[0]} to {generations[-1]}")
        lines.append("=" * self.separator_width)

        return "\n".join(lines)
