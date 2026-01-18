"""Game loop management."""

import time
from pydantic import BaseModel, Field
from pyevolvesim.life_game.grid import Grid
from pyevolvesim.life_game.renderer import Renderer


class Game(BaseModel):
    """Manages the game loop and state.

    Attributes:
        grid: The game grid
        renderer: The renderer for display
        generation: Current generation number
        delay: Delay between generations in seconds
    """

    grid: Grid = Field(description="The game grid")
    renderer: Renderer = Field(default_factory=Renderer)
    generation: int = Field(default=0, ge=0, description="Current generation")
    delay: float = Field(default=0.1, gt=0, description="Delay between generations")

    def step(self) -> None:
        """Advance to the next generation."""
        self.grid = self.grid.next_generation()
        self.generation += 1

    def run(self, max_generations: int | None = None) -> None:
        """Run the game loop.

        Args:
            max_generations: Maximum number of generations to run.
                           If None, runs indefinitely until interrupted.
        """
        try:
            while max_generations is None or self.generation < max_generations:
                self.renderer.render(self.grid, self.generation)
                time.sleep(self.delay)
                self.step()

                # Stop if all cells are dead
                if not self.grid.alive_cells:
                    self.renderer.render(self.grid, self.generation)
                    print("\nAll cells died. Game over.")
                    break

        except KeyboardInterrupt:
            print("\n\nGame interrupted by user.")
        finally:
            print(f"Final generation: {self.generation}")
            print(f"Alive cells: {len(self.grid.alive_cells)}")

    class Config:
        frozen = False
        arbitrary_types_allowed = True
