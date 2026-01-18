"""Grid module for managing cell states and evolution."""

from typing import Set, Tuple
from pydantic import BaseModel, Field, field_validator


Coordinate = Tuple[int, int]


class Grid(BaseModel):
    """Represents the game grid and handles cell evolution.

    Attributes:
        width: Grid width
        height: Grid height
        alive_cells: Set of coordinates of alive cells
    """

    width: int = Field(gt=0, description="Grid width")
    height: int = Field(gt=0, description="Grid height")
    alive_cells: Set[Coordinate] = Field(default_factory=set)

    @field_validator("width", "height")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Dimensions must be positive")
        return v

    def is_alive(self, x: int, y: int) -> bool:
        """Check if a cell is alive."""
        return (x, y) in self.alive_cells

    def set_alive(self, x: int, y: int) -> None:
        """Set a cell as alive."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.alive_cells.add((x, y))

    def set_dead(self, x: int, y: int) -> None:
        """Set a cell as dead."""
        self.alive_cells.discard((x, y))

    def count_alive_neighbors(self, x: int, y: int) -> int:
        """Count alive neighbors for a cell.

        Uses Moore neighborhood (8 adjacent cells).
        """
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.is_alive(nx, ny):
                        count += 1
        return count

    def next_generation(self) -> "Grid":
        """Calculate the next generation based on Conway's rules.

        Rules:
        1. Any live cell with 2-3 live neighbors survives
        2. Any dead cell with exactly 3 live neighbors becomes alive
        3. All other cells die or stay dead
        """
        new_alive_cells: Set[Coordinate] = set()

        # Check all cells that might change state
        # (alive cells and their neighbors)
        cells_to_check: Set[Coordinate] = set()

        for x, y in self.alive_cells:
            cells_to_check.add((x, y))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        cells_to_check.add((nx, ny))

        for x, y in cells_to_check:
            neighbors = self.count_alive_neighbors(x, y)
            is_currently_alive = self.is_alive(x, y)

            if is_currently_alive and neighbors in [2, 3]:
                new_alive_cells.add((x, y))
            elif not is_currently_alive and neighbors == 3:
                new_alive_cells.add((x, y))

        return Grid(width=self.width, height=self.height, alive_cells=new_alive_cells)

    class Config:
        frozen = False
