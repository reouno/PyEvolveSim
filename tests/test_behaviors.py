"""Unit tests for creature behavior logic.

These tests verify that behavior functions correctly handle decision-making,
pathfinding, and action selection for creatures.
"""

from life_game.evolution.behaviors import (
    find_visible_foods,
    get_closest_food,
    move_towards,
    random_move,
    can_reproduce,
    find_empty_neighbor,
    decide_action,
)
from life_game.evolution.creature import Creature, Genes
from life_game.evolution.food import Food
from life_game.evolution.world import EvolutionWorld


class TestFindVisibleFoods:
    """Test finding foods within vision range."""

    def test_empty_world(self):
        """No foods in world returns empty list."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes(vision_range=3))
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        visible = find_visible_foods(creature, world)
        assert visible == []

    def test_food_within_vision_range(self):
        """Food within vision range should be found."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes(vision_range=3))
        food = Food(x=6, y=6, energy=10.0)  # Manhattan distance = 2
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[food])

        visible = find_visible_foods(creature, world)
        assert len(visible) == 1
        assert visible[0] == food

    def test_food_outside_vision_range(self):
        """Food outside vision range should not be found."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes(vision_range=2))
        food = Food(x=10, y=10, energy=10.0)  # Manhattan distance = 10
        world = EvolutionWorld(width=15, height=15, creatures=[creature], foods=[food])

        visible = find_visible_foods(creature, world)
        assert visible == []

    def test_food_at_exact_vision_boundary(self):
        """Food at exact vision range boundary should be included."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes(vision_range=3))
        food = Food(
            x=7, y=6, energy=10.0
        )  # Manhattan distance = 3 (exactly at boundary)
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[food])

        visible = find_visible_foods(creature, world)
        assert len(visible) == 1
        assert visible[0] == food

    def test_multiple_foods_mixed_ranges(self):
        """Multiple foods at different distances filters correctly."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes(vision_range=3))
        food_close = Food(x=6, y=5, energy=10.0)  # Distance = 1
        food_medium = Food(x=7, y=6, energy=10.0)  # Distance = 3
        food_far = Food(x=10, y=10, energy=10.0)  # Distance = 10
        world = EvolutionWorld(
            width=15,
            height=15,
            creatures=[creature],
            foods=[food_close, food_medium, food_far],
        )

        visible = find_visible_foods(creature, world)
        assert len(visible) == 2
        assert food_close in visible
        assert food_medium in visible
        assert food_far not in visible

    def test_vision_range_one(self):
        """Vision range of 1 only sees immediate neighbors."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes(vision_range=1))
        food_adjacent = Food(x=6, y=5, energy=10.0)  # Distance = 1
        food_diagonal = Food(x=6, y=6, energy=10.0)  # Distance = 2 (diagonal)
        world = EvolutionWorld(
            width=10,
            height=10,
            creatures=[creature],
            foods=[food_adjacent, food_diagonal],
        )

        visible = find_visible_foods(creature, world)
        assert len(visible) == 1
        assert visible[0] == food_adjacent


class TestGetClosestFood:
    """Test finding the closest food from a list."""

    def test_empty_list_returns_none(self):
        """Empty food list returns None."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        closest = get_closest_food(creature, [])
        assert closest is None

    def test_single_food_returns_it(self):
        """Single food in list returns that food."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        food = Food(x=7, y=7, energy=10.0)
        closest = get_closest_food(creature, [food])
        assert closest == food

    def test_multiple_foods_returns_nearest(self):
        """Multiple foods returns the nearest one."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        food_far = Food(x=10, y=10, energy=10.0)  # Distance = 10
        food_near = Food(x=6, y=6, energy=10.0)  # Distance = 2
        food_medium = Food(x=8, y=5, energy=10.0)  # Distance = 3

        closest = get_closest_food(creature, [food_far, food_near, food_medium])
        assert closest == food_near

    def test_equidistant_foods_returns_one(self):
        """Equidistant foods returns one of them (first by min())."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        food1 = Food(x=6, y=5, energy=10.0)  # Distance = 1
        food2 = Food(x=5, y=6, energy=10.0)  # Distance = 1

        closest = get_closest_food(creature, [food1, food2])
        # Should return one of them consistently
        assert closest in [food1, food2]


class TestMoveTowards:
    """Test pathfinding towards a target."""

    def test_move_horizontal_right(self):
        """Move right towards target."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        action = move_towards(creature, target_x=8, target_y=5, world=world)
        assert action == (1, 0)  # Move right

    def test_move_horizontal_left(self):
        """Move left towards target."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        action = move_towards(creature, target_x=2, target_y=5, world=world)
        assert action == (-1, 0)  # Move left

    def test_move_vertical_up(self):
        """Move up towards target."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        action = move_towards(creature, target_x=5, target_y=2, world=world)
        assert action == (0, -1)  # Move up

    def test_move_vertical_down(self):
        """Move down towards target."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        action = move_towards(creature, target_x=5, target_y=8, world=world)
        assert action == (0, 1)  # Move down

    def test_move_diagonal_prioritizes_larger_axis(self):
        """Diagonal movement prioritizes axis with larger distance."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        # Target is further right (3) than down (1)
        action = move_towards(creature, target_x=8, target_y=6, world=world)
        assert action == (1, 0)  # Should prioritize horizontal

    def test_blocked_horizontal_tries_vertical(self):
        """Blocked horizontal path tries vertical."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        blocker = Creature(id=2, x=6, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(
            width=10, height=10, creatures=[creature, blocker], foods=[]
        )

        # Target is to the right, but path is blocked
        action = move_towards(creature, target_x=8, target_y=6, world=world)
        assert action == (0, 1)  # Should try vertical instead

    def test_blocked_vertical_tries_horizontal(self):
        """Blocked vertical path tries horizontal."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        blocker = Creature(id=2, x=5, y=6, energy=100.0, genes=Genes())
        world = EvolutionWorld(
            width=10, height=10, creatures=[creature, blocker], foods=[]
        )

        # Target is below, but path is blocked
        action = move_towards(creature, target_x=6, target_y=8, world=world)
        assert action == (1, 0)  # Should try horizontal instead

    def test_all_paths_blocked_stays_still(self):
        """All paths blocked returns (0, 0)."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        blocker_right = Creature(id=2, x=6, y=5, energy=100.0, genes=Genes())
        blocker_down = Creature(id=3, x=5, y=6, energy=100.0, genes=Genes())
        world = EvolutionWorld(
            width=10,
            height=10,
            creatures=[creature, blocker_right, blocker_down],
            foods=[],
        )

        # Target is to the right and down, both blocked
        action = move_towards(creature, target_x=8, target_y=8, world=world)
        assert action == (0, 0)  # Stay in place

    def test_at_edge_of_world(self):
        """Movement at world edge respects bounds."""
        creature = Creature(id=1, x=0, y=0, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        # Try to move left (would go out of bounds)
        action = move_towards(creature, target_x=-1, target_y=0, world=world)
        assert action == (0, 0)  # Can't move out of bounds


class TestRandomMove:
    """Test random movement behavior."""

    def test_returns_valid_move(self):
        """Random move returns a valid move from possible options."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        action = random_move(creature, world)
        # Should be one of the valid moves
        assert action in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def test_avoids_occupied_positions(self):
        """Random move avoids positions with other creatures."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        blocker = Creature(id=2, x=6, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(
            width=10, height=10, creatures=[creature, blocker], foods=[]
        )

        # Run multiple times to test randomness
        for _ in range(10):
            action = random_move(creature, world)
            # Should never try to move right (where blocker is)
            assert action != (1, 0)

    def test_all_positions_blocked_stays_still(self):
        """All positions blocked returns (0, 0)."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        blockers = [
            Creature(id=2, x=4, y=5, energy=100.0, genes=Genes()),  # left
            Creature(id=3, x=6, y=5, energy=100.0, genes=Genes()),  # right
            Creature(id=4, x=5, y=4, energy=100.0, genes=Genes()),  # up
            Creature(id=5, x=5, y=6, energy=100.0, genes=Genes()),  # down
        ]
        world = EvolutionWorld(
            width=10, height=10, creatures=[creature] + blockers, foods=[]
        )

        action = random_move(creature, world)
        assert action == (0, 0)


class TestCanReproduce:
    """Test reproduction eligibility."""

    def test_enough_energy_and_age_can_reproduce(self):
        """Creature with enough energy and age can reproduce."""
        # Default max_energy is 200, 60% threshold = 120
        # MIN_REPRODUCTION_AGE is 5
        creature = Creature(id=1, x=5, y=5, energy=125.0, age=5, genes=Genes())
        assert can_reproduce(creature) is True

    def test_low_energy_cannot_reproduce(self):
        """Creature with low energy cannot reproduce."""
        creature = Creature(id=1, x=5, y=5, energy=50.0, age=5, genes=Genes())
        assert can_reproduce(creature) is False

    def test_young_age_cannot_reproduce(self):
        """Creature too young cannot reproduce."""
        # MIN_REPRODUCTION_AGE is 5
        creature = Creature(id=1, x=5, y=5, energy=100.0, age=4, genes=Genes())
        assert can_reproduce(creature) is False

    def test_at_exact_threshold_can_reproduce(self):
        """Creature at exact threshold can reproduce."""
        # Default max_energy is 200, 60% = 120
        creature = Creature(id=1, x=5, y=5, energy=120.0, age=5, genes=Genes())
        assert can_reproduce(creature) is True

    def test_different_max_energy_adjusts_threshold(self):
        """Threshold adjusts based on max_energy gene."""
        # max_energy = 250, 60% = 150
        genes = Genes(max_energy=250.0)
        creature = Creature(id=1, x=5, y=5, energy=155.0, age=5, genes=genes)
        assert can_reproduce(creature) is True

        creature_below = Creature(id=2, x=5, y=5, energy=145.0, age=5, genes=genes)
        assert can_reproduce(creature_below) is False


class TestFindEmptyNeighbor:
    """Test finding empty neighboring positions."""

    def test_empty_neighbor_found(self):
        """Empty neighbor position is found."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        neighbor = find_empty_neighbor(5, 5, world)
        assert neighbor is not None
        # Should be one of the 4 neighbors
        assert neighbor in [(4, 5), (6, 5), (5, 4), (5, 6)]

    def test_all_neighbors_occupied_returns_none(self):
        """All neighbors occupied returns None."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        blockers = [
            Creature(id=2, x=4, y=5, energy=100.0, genes=Genes()),
            Creature(id=3, x=6, y=5, energy=100.0, genes=Genes()),
            Creature(id=4, x=5, y=4, energy=100.0, genes=Genes()),
            Creature(id=5, x=5, y=6, energy=100.0, genes=Genes()),
        ]
        world = EvolutionWorld(
            width=10, height=10, creatures=[creature] + blockers, foods=[]
        )

        neighbor = find_empty_neighbor(5, 5, world)
        assert neighbor is None

    def test_at_world_edge(self):
        """At world edge, only valid neighbors are considered."""
        creature = Creature(id=1, x=0, y=0, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        neighbor = find_empty_neighbor(0, 0, world)
        assert neighbor is not None
        # Only right and down are valid
        assert neighbor in [(1, 0), (0, 1)]

    def test_randomization(self):
        """Multiple calls return different neighbors (tests randomization)."""
        creature = Creature(id=1, x=5, y=5, energy=100.0, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        results = set()
        for _ in range(20):
            neighbor = find_empty_neighbor(5, 5, world)
            if neighbor:
                results.add(neighbor)

        # Should get at least 2 different neighbors over 20 calls
        assert len(results) >= 2


class TestDecideAction:
    """Test the main decision-making function."""

    def test_prioritizes_reproduction(self):
        """Reproduction is highest priority when eligible."""
        genes = Genes()
        # Energy at 60% of max_energy (200 * 0.6 = 120), MIN_REPRODUCTION_AGE is 5
        creature = Creature(id=1, x=5, y=5, energy=125.0, age=5, genes=genes)
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        action = decide_action(creature, world)
        assert action == (-1, -1)  # Reproduction signal

    def test_seeks_visible_food_when_not_reproducing(self):
        """Creature seeks visible food when not ready to reproduce."""
        creature = Creature(
            id=1, x=5, y=5, energy=50.0, age=5, genes=Genes(vision_range=5)
        )
        food = Food(x=7, y=5, energy=10.0)
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[food])

        action = decide_action(creature, world)
        # Should move towards food (to the right)
        assert action == (1, 0)

    def test_random_move_when_no_food_visible(self):
        """Creature moves randomly when no food is visible."""
        creature = Creature(
            id=1, x=5, y=5, energy=50.0, age=5, genes=Genes(vision_range=2)
        )
        food = Food(x=10, y=10, energy=10.0)  # Too far to see
        world = EvolutionWorld(width=15, height=15, creatures=[creature], foods=[food])

        action = decide_action(creature, world)
        # Should be a random move (not reproduction signal)
        assert action != (-1, -1)
        assert action in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def test_empty_world_random_move(self):
        """Creature moves randomly in empty world."""
        creature = Creature(id=1, x=5, y=5, energy=50.0, age=5, genes=Genes())
        world = EvolutionWorld(width=10, height=10, creatures=[creature], foods=[])

        action = decide_action(creature, world)
        # Should be a random move
        assert action in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
