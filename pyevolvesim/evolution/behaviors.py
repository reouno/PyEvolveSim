"""Pure functions for creature behavior logic."""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .creature import Creature
    from .food import Food
    from .world import EvolutionWorld


# Action types: (dx, dy) where dx, dy are -1, 0, or 1
# Special case: (-1, -1) means "reproduce"
Action = tuple[int, int]
Coordinate = tuple[int, int]


def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Manhattan distance between two positions."""
    return abs(x2 - x1) + abs(y2 - y1)


def find_visible_foods(creature: "Creature", world: "EvolutionWorld") -> list["Food"]:
    """Return all foods within the creature's vision range."""
    visible_foods = []
    vision_range = creature.genes.vision_range

    for food in world.foods:
        distance = manhattan_distance(creature.x, creature.y, food.x, food.y)
        if distance <= vision_range:
            visible_foods.append(food)

    return visible_foods


def get_closest_food(creature: "Creature", foods: list["Food"]) -> "Food | None":
    """Return the closest food to the creature, or None if no foods."""
    if not foods:
        return None

    def distance(food: "Food") -> int:
        return manhattan_distance(creature.x, creature.y, food.x, food.y)

    return min(foods, key=distance)


def move_towards(
    creature: "Creature", target_x: int, target_y: int, world: "EvolutionWorld"
) -> Action:
    """
    Return an action to move one step towards the target.
    Prioritizes the axis with larger distance.
    """
    dx = target_x - creature.x
    dy = target_y - creature.y

    # Normalize to -1, 0, or 1
    move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    move_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    # Try moving on the axis with larger absolute distance first
    if abs(dx) >= abs(dy):
        # Try horizontal move
        new_x = creature.x + move_x
        new_y = creature.y
        if (
            world.is_valid_position(new_x, new_y)
            and world.get_creature_at(new_x, new_y) is None
        ):
            return (move_x, 0)
        # Try vertical move
        new_x = creature.x
        new_y = creature.y + move_y
        if (
            world.is_valid_position(new_x, new_y)
            and world.get_creature_at(new_x, new_y) is None
        ):
            return (0, move_y)
    else:
        # Try vertical move first
        new_x = creature.x
        new_y = creature.y + move_y
        if (
            world.is_valid_position(new_x, new_y)
            and world.get_creature_at(new_x, new_y) is None
        ):
            return (0, move_y)
        # Try horizontal move
        new_x = creature.x + move_x
        new_y = creature.y
        if (
            world.is_valid_position(new_x, new_y)
            and world.get_creature_at(new_x, new_y) is None
        ):
            return (move_x, 0)

    # If both blocked, stay in place
    return (0, 0)


def random_move(creature: "Creature", world: "EvolutionWorld") -> Action:
    """Return a random valid move action."""
    possible_moves = [
        (-1, 0),  # left
        (1, 0),  # right
        (0, -1),  # up
        (0, 1),  # down
        (0, 0),  # stay
    ]

    # Shuffle to randomize
    random.shuffle(possible_moves)

    for dx, dy in possible_moves:
        new_x = creature.x + dx
        new_y = creature.y + dy
        if (
            world.is_valid_position(new_x, new_y)
            and world.get_creature_at(new_x, new_y) is None
        ):
            return (dx, dy)

    # If all blocked, stay in place
    return (0, 0)


def can_reproduce(creature: "Creature") -> bool:
    """
    Check if the creature has enough energy and age to reproduce.
    Uses percentage-based threshold: creatures reproduce at 60% of max_energy.
    This creates r/K selection: small creatures reproduce faster, large creatures survive longer.
    """
    from .config import MIN_REPRODUCTION_AGE

    # Reproduce when energy reaches 60% of max capacity
    threshold_percentage = 0.6
    effective_threshold = creature.genes.max_energy * threshold_percentage

    return (
        creature.energy >= effective_threshold and creature.age >= MIN_REPRODUCTION_AGE
    )


def find_empty_neighbor(x: int, y: int, world: "EvolutionWorld") -> Coordinate | None:
    """Find an empty neighboring position, or None if all occupied."""
    neighbors = [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
    ]

    # Shuffle to randomize placement
    random.shuffle(neighbors)

    for nx, ny in neighbors:
        if world.is_valid_position(nx, ny) and world.get_creature_at(nx, ny) is None:
            return (nx, ny)

    return None


def decide_action(creature: "Creature", world: "EvolutionWorld") -> Action:
    """
    Decide what action the creature should take.
    Priority:
    1. Reproduce if enough energy
    2. Move towards visible food
    3. Random move
    """
    # Check if can reproduce
    if can_reproduce(creature):
        # Return special action (-1, -1) to signal reproduction
        return (-1, -1)

    # Look for visible food
    visible_foods = find_visible_foods(creature, world)
    if visible_foods:
        closest_food = get_closest_food(creature, visible_foods)
        if closest_food:
            return move_towards(creature, closest_food.x, closest_food.y, world)

    # No food in sight, move randomly
    return random_move(creature, world)
