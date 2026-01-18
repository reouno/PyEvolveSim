"""Unit tests for graph rendering.

Tests verify that GraphRenderer correctly formats and renders data
while maintaining independence from data collection concerns.
"""

import pytest
from life_game.evolution.graph_renderer import GraphRenderer, GraphDisplay


class TestGraphRenderer:
    """Test GraphRenderer functionality."""

    def test_initialization(self):
        """Test renderer initialization."""
        renderer = GraphRenderer(height=10, width=50)

        assert renderer.height == 10
        assert renderer.width == 50

    def test_sparkline_with_empty_data(self):
        """Test sparkline rendering with empty data."""
        renderer = GraphRenderer()
        lines = renderer.render_sparkline([], "Test")

        assert len(lines) > 0
        assert "no data" in lines[0].lower()

    def test_sparkline_with_single_value(self):
        """Test sparkline with a single value."""
        renderer = GraphRenderer()
        lines = renderer.render_sparkline([5.0], "Speed")

        assert len(lines) > 0
        assert "Speed" in lines[0]
        assert "5.00" in lines[0]

    def test_sparkline_with_multiple_values(self):
        """Test sparkline with multiple values."""
        renderer = GraphRenderer()
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        lines = renderer.render_sparkline(values, "Speed")

        assert len(lines) >= 3  # Label, sparkline, axis
        assert "Speed" in lines[0]
        assert "5.00" in lines[0]  # Latest value

    def test_sparkline_respects_width_limit(self):
        """Test that sparkline respects width limit."""
        renderer = GraphRenderer(width=10)
        values = [float(i) for i in range(50)]  # 50 values

        lines = renderer.render_sparkline(values, "Test")

        # Sparkline should not exceed width
        sparkline = lines[1]
        assert len(sparkline) <= 10

    def test_sparkline_with_min_max_specified(self):
        """Test sparkline with specified min/max values."""
        renderer = GraphRenderer()
        values = [1.0, 2.0, 3.0]

        lines = renderer.render_sparkline(values, "Speed", min_val=0.0, max_val=5.0)

        assert len(lines) > 0
        # Should scale to specified range, not data range

    def test_sparkline_with_constant_values(self):
        """Test sparkline when all values are the same."""
        renderer = GraphRenderer()
        values = [5.0, 5.0, 5.0, 5.0]

        lines = renderer.render_sparkline(values, "Speed")

        assert len(lines) > 0
        assert "5.00" in lines[0]


class TestGraphDisplay:
    """Test GraphDisplay high-level interface."""

    def test_initialization(self):
        """Test GraphDisplay initialization."""
        renderer = GraphRenderer()
        display = GraphDisplay(renderer)

        assert display.renderer is renderer

    def test_render_evolution_graphs_empty(self):
        """Test rendering with empty data."""
        renderer = GraphRenderer()
        display = GraphDisplay(renderer)

        output = display.render_evolution_graphs([], [], [], [])

        assert "Collecting data" in output

    def test_render_evolution_graphs_with_data(self):
        """Test rendering with valid data."""
        renderer = GraphRenderer()
        display = GraphDisplay(renderer)

        generations = [0, 10, 20]
        creature_counts = [10.0, 20.0, 30.0]
        avg_speeds = [1.0, 1.5, 2.0]
        std_speeds = [0.5, 0.6, 0.7]

        output = display.render_evolution_graphs(
            generations, creature_counts, avg_speeds, std_speeds
        )

        assert "Evolution Statistics" in output
        assert "Population" in output
        assert "Avg Speed" in output
        assert "Speed Diversity" in output
        assert "0 to 20" in output  # Generation range


class TestGraphRendererEdgeCases:
    """Test edge cases and special conditions."""

    def test_sparkline_with_negative_values(self):
        """Test sparkline can handle negative values."""
        renderer = GraphRenderer()
        values = [-5.0, -3.0, 0.0, 2.0, 5.0]

        lines = renderer.render_sparkline(values, "Test")

        assert len(lines) > 0
        # Should not crash with negative values

    def test_sparkline_with_very_large_values(self):
        """Test sparkline with large values."""
        renderer = GraphRenderer()
        values = [1000.0, 2000.0, 3000.0]

        lines = renderer.render_sparkline(values, "Large")

        assert len(lines) > 0
        assert "3000.00" in lines[0]

    def test_sparkline_with_very_small_range(self):
        """Test sparkline with values in small range."""
        renderer = GraphRenderer()
        values = [1.001, 1.002, 1.003]

        lines = renderer.render_sparkline(values, "Precise")

        assert len(lines) > 0
        # Should handle small variations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
