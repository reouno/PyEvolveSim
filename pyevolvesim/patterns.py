"""Initial pattern definitions for the Game of Life."""

import random
from typing import List
from pydantic import BaseModel, Field
from pyevolvesim.grid import Grid, Coordinate


class Pattern(BaseModel):
    """Represents an initial pattern.

    Attributes:
        name: Pattern name
        cells: List of relative coordinates (x, y) for alive cells
        description: Pattern description
    """

    name: str = Field(description="Pattern name")
    cells: List[Coordinate] = Field(description="List of alive cell coordinates")
    description: str = Field(default="", description="Pattern description")

    def apply_to_grid(self, grid: Grid, offset_x: int = 0, offset_y: int = 0) -> None:
        """Apply this pattern to a grid at the given offset.

        Args:
            grid: The grid to apply the pattern to
            offset_x: X offset for pattern placement
            offset_y: Y offset for pattern placement
        """
        for x, y in self.cells:
            grid.set_alive(offset_x + x, offset_y + y)


# Famous patterns

GLIDER = Pattern(
    name="Glider",
    cells=[(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)],
    description="A small spaceship that travels diagonally",
)

BLINKER = Pattern(
    name="Blinker", cells=[(0, 0), (1, 0), (2, 0)], description="A period-2 oscillator"
)

TOAD = Pattern(
    name="Toad",
    cells=[(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1)],
    description="A period-2 oscillator",
)

BEACON = Pattern(
    name="Beacon",
    cells=[(0, 0), (1, 0), (0, 1), (3, 2), (2, 3), (3, 3)],
    description="A period-2 oscillator",
)

PULSAR = Pattern(
    name="Pulsar",
    cells=[
        # Top section
        (2, 0),
        (3, 0),
        (4, 0),
        (8, 0),
        (9, 0),
        (10, 0),
        (0, 2),
        (5, 2),
        (7, 2),
        (12, 2),
        (0, 3),
        (5, 3),
        (7, 3),
        (12, 3),
        (0, 4),
        (5, 4),
        (7, 4),
        (12, 4),
        (2, 5),
        (3, 5),
        (4, 5),
        (8, 5),
        (9, 5),
        (10, 5),
        # Bottom section
        (2, 7),
        (3, 7),
        (4, 7),
        (8, 7),
        (9, 7),
        (10, 7),
        (0, 8),
        (5, 8),
        (7, 8),
        (12, 8),
        (0, 9),
        (5, 9),
        (7, 9),
        (12, 9),
        (0, 10),
        (5, 10),
        (7, 10),
        (12, 10),
        (2, 12),
        (3, 12),
        (4, 12),
        (8, 12),
        (9, 12),
        (10, 12),
    ],
    description="A period-3 oscillator",
)

GOSPER_GLIDER_GUN = Pattern(
    name="Gosper Glider Gun",
    cells=[
        # Left square
        (0, 4),
        (0, 5),
        (1, 4),
        (1, 5),
        # Left circle
        (10, 4),
        (10, 5),
        (10, 6),
        (11, 3),
        (11, 7),
        (12, 2),
        (12, 8),
        (13, 2),
        (13, 8),
        (14, 5),
        (15, 3),
        (15, 7),
        (16, 4),
        (16, 5),
        (16, 6),
        (17, 5),
        # Right section
        (20, 2),
        (20, 3),
        (20, 4),
        (21, 2),
        (21, 3),
        (21, 4),
        (22, 1),
        (22, 5),
        (24, 0),
        (24, 1),
        (24, 5),
        (24, 6),
        # Right square
        (34, 2),
        (34, 3),
        (35, 2),
        (35, 3),
    ],
    description="A pattern that continuously produces gliders",
)


def create_random_grid(width: int, height: int, density: float = 0.3) -> Grid:
    """Create a grid with random alive cells.

    Args:
        width: Grid width
        height: Grid height
        density: Probability of a cell being alive (0.0 to 1.0)

    Returns:
        A Grid with randomly placed alive cells
    """
    grid = Grid(width=width, height=height)
    for x in range(width):
        for y in range(height):
            if random.random() < density:
                grid.set_alive(x, y)
    return grid


def create_grid_with_pattern(
    width: int, height: int, pattern: Pattern, center: bool = True
) -> Grid:
    """Create a grid with a specific pattern.

    Args:
        width: Grid width
        height: Grid height
        pattern: The pattern to place
        center: If True, center the pattern in the grid

    Returns:
        A Grid with the pattern placed
    """
    grid = Grid(width=width, height=height)

    if center:
        # Calculate pattern dimensions
        if pattern.cells:
            min_x = min(x for x, _ in pattern.cells)
            max_x = max(x for x, _ in pattern.cells)
            min_y = min(y for _, y in pattern.cells)
            max_y = max(y for _, y in pattern.cells)

            pattern_width = max_x - min_x + 1
            pattern_height = max_y - min_y + 1

            offset_x = (width - pattern_width) // 2 - min_x
            offset_y = (height - pattern_height) // 2 - min_y
        else:
            offset_x = width // 2
            offset_y = height // 2
    else:
        offset_x = 0
        offset_y = 0

    pattern.apply_to_grid(grid, offset_x, offset_y)
    return grid
