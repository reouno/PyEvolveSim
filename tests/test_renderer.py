"""Tests for atomic rendering functionality."""

from life_game.evolution.renderer import EvolutionRenderer
from life_game.evolution.world import EvolutionWorld
from life_game.evolution.stats import WorldStats
from life_game.evolution.creature import Creature, Genes
from life_game.evolution.config import INITIAL_ENERGY


def test_render_returns_string():
    """Verify render returns string, not None."""
    world = EvolutionWorld(width=50, height=30)
    stats = WorldStats.from_world(world)
    renderer = EvolutionRenderer()

    result = renderer.render(world, stats)

    assert isinstance(result, str)
    assert len(result) > 0


def test_render_contains_generation():
    """Verify generation number appears in output."""
    world = EvolutionWorld(width=50, height=30)
    world.generation = 42
    stats = WorldStats.from_world(world)
    renderer = EvolutionRenderer()

    result = renderer.render(world, stats)

    assert "Gen 42" in result


def test_clear_screen_returns_string():
    """Verify terminal control codes returned as string."""
    result = EvolutionRenderer.clear_screen()

    assert isinstance(result, str)
    assert "\033[2J\033[H\033[?25l" == result


def test_show_cursor_returns_string():
    """Verify cursor show code returned as string."""
    result = EvolutionRenderer.show_cursor()

    assert isinstance(result, str)
    assert "\033[?25h" == result


def test_render_no_creatures():
    """Verify render handles empty world gracefully."""
    world = EvolutionWorld(width=50, height=30)
    world.creatures = []  # No creatures
    stats = WorldStats.from_world(world)
    renderer = EvolutionRenderer()

    result = renderer.render(world, stats)

    assert isinstance(result, str)
    # Should not crash, should contain extinction message
    assert "All creatures have died" in result or "Creatures:   0" in result


def test_render_contains_statistics():
    """Verify render output contains expected statistics sections."""
    world = EvolutionWorld(width=50, height=30)
    # Add a creature so stats are displayed
    creature = Creature(
        x=10,
        y=10,
        energy=INITIAL_ENERGY,
        genes=Genes(),
        id=0,
    )
    world.creatures.append(creature)
    stats = WorldStats.from_world(world)
    renderer = EvolutionRenderer()

    result = renderer.render(world, stats)

    # Check for key sections
    assert "Creatures:" in result
    assert "Food:" in result
    assert "Spawn:" in result
    assert "Press Ctrl+C to exit" in result


def test_render_output_has_proper_structure():
    """Verify render output is properly formatted with newlines."""
    world = EvolutionWorld(width=50, height=30)
    stats = WorldStats.from_world(world)
    renderer = EvolutionRenderer()

    result = renderer.render(world, stats)

    lines = result.split("\n")

    # Should have multiple lines
    assert len(lines) > 10

    # First line should be header separator
    assert "=" in lines[0]

    # Should contain Evolution Simulation line
    assert any("Evolution Simulation" in line for line in lines)
