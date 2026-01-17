"""Renderer module for terminal display."""

import os
from pydantic import BaseModel, Field
from life_game.grid import Grid


class Renderer(BaseModel):
    """Handles rendering the grid to the terminal.

    Attributes:
        alive_char: Character to display for alive cells
        dead_char: Character to display for dead cells
    """

    alive_char: str = Field(default="■", description="Character for alive cells")
    dead_char: str = Field(default="･", description="Character for dead cells")

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system("clear" if os.name != "nt" else "cls")

    def render(self, grid: Grid, generation: int = 0) -> None:
        """Render the grid to the terminal.

        Args:
            grid: The grid to render
            generation: Current generation number
        """
        self.clear_screen()

        # Header
        print(f"Conway's Game of Life - Generation: {generation}")
        print("=" * (grid.width * 2))

        # Grid
        for y in range(grid.height):
            line = ""
            for x in range(grid.width):
                if grid.is_alive(x, y):
                    line += self.alive_char + " "
                else:
                    line += self.dead_char + " "
            print(line)

        # Footer
        print("=" * (grid.width * 2))
        print("Press Ctrl+C to exit")

    class Config:
        frozen = False
