"""Rendering for the evolution simulation."""

from .world import EvolutionWorld
from .stats import WorldStats


class EvolutionRenderer:
    """Renders the evolution world to the terminal."""

    @staticmethod
    def clear_screen() -> str:
        """Return terminal codes to clear screen and hide cursor."""
        return "\033[2J\033[H\033[?25l"

    @staticmethod
    def show_cursor() -> str:
        """Return terminal code to show cursor."""
        return "\033[?25h"

    @staticmethod
    def render(world: EvolutionWorld, stats: WorldStats) -> str:
        """Build world frame as string (pure function, no printing)."""
        lines: list[str] = []

        # Header
        lines.append("=" * (world.width + 2))
        lines.append(
            f"Evolution Simulation - Gen {stats.generation} | Press Ctrl+C to exit"
        )

        # Create grid
        grid = [["･" for _ in range(world.width)] for _ in range(world.height)]

        # Place food
        for food in world.foods:
            grid[food.y][food.x] = "F"

        # Place creatures (overwrite food if on same position)
        # Display creature's vision range to visualize evolution
        for creature in world.creatures:
            vision = min(creature.genes.vision_range, 9)  # Cap at 9 for single digit
            grid[creature.y][creature.x] = str(vision)

        # Append all grid rows
        for row in grid:
            lines.append("".join(row))

        # Statistics section
        lines.append("=" * (world.width + 2))
        if stats.creature_count > 0:
            lines.append(
                f"Creatures: {stats.creature_count:2d} | Food: {stats.food_count:2d} | "
                f"Spawn: {stats.current_food_spawn_rate:.1f} | "
                f"Energy: {stats.avg_energy:.1f} | Age: {stats.avg_age:.1f}"
            )
            lines.append("─" * (world.width + 2))
            lines.append(
                f"Traits (avg/σ): Speed: {stats.avg_speed:.2f}/{stats.std_speed:.2f} | "
                f"Vision: {stats.avg_vision_range:.2f}/{stats.std_vision_range:.2f} | "
                f"Move: {stats.avg_move_cost:.2f}/{stats.std_move_cost:.2f}"
            )
            lines.append(
                f"                Metab: {stats.avg_metabolism:.2f}/{stats.std_metabolism:.2f} | "
                f"MaxE: {stats.avg_max_energy:.1f}/{stats.std_max_energy:.1f} | "
                f"Food: {stats.avg_food_efficiency:.2f}/{stats.std_food_efficiency:.2f}"
            )
        else:
            lines.append("Creatures: 0 | All creatures have died. Simulation ended.")

        lines.append("=" * (world.width + 2))

        return "\n".join(lines)
