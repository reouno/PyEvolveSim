"""EvolutionWorld class managing the simulation state."""

import math
import random
from pydantic import BaseModel, Field

from .creature import Creature
from .food import Food
from . import behaviors
from .config import (
    FOOD_ENERGY,
    MAX_FOOD,
    FOOD_SPAWN_PER_TURN,
    NUM_FOOD_CLUSTERS,
    CLUSTER_SPREAD,
    CLUSTER_MOVE_INTERVAL,
    ENABLE_TEMPORAL_VARIATION,
    SEASON_CYCLE_LENGTH,
    SEASON_MIN_SPAWN_RATE,
    SEASON_MAX_SPAWN_RATE,
)


class EvolutionWorld(BaseModel):
    """The world containing creatures and food."""

    width: int = Field(ge=1)
    height: int = Field(ge=1)
    creatures: list[Creature] = Field(default_factory=list)
    foods: list[Food] = Field(default_factory=list)
    generation: int = Field(default=0, ge=0)
    next_creature_id: int = Field(default=0, ge=0)
    food_clusters: list[tuple[int, int]] = Field(default_factory=list)

    def get_creature_at(self, x: int, y: int) -> Creature | None:
        """Return the creature at the specified position, or None."""
        for creature in self.creatures:
            if creature.x == x and creature.y == y:
                return creature
        return None

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is within world bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def initialize_food_clusters(self) -> None:
        """Create random cluster centers for food spawning."""
        self.food_clusters = [
            (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            for _ in range(NUM_FOOD_CLUSTERS)
        ]

    def spawn_food_near_cluster(
        self,
        occupied_positions: set[tuple[int, int]],
        food_positions: set[tuple[int, int]],
    ) -> Food | None:
        """
        Spawn food near a random cluster center.
        Returns None if unable to find valid position after attempts.
        """
        if not self.food_clusters:
            self.initialize_food_clusters()

        # Pick a random cluster
        cluster_x, cluster_y = random.choice(self.food_clusters)

        # Try multiple times to find a valid position near this cluster
        for _ in range(20):
            # Distance from cluster (exponential distribution for clustering effect)
            distance = int(random.expovariate(CLUSTER_SPREAD))

            # Random angle
            angle = random.uniform(0, 2 * math.pi)

            # Calculate position
            fx = int(cluster_x + distance * math.cos(angle))
            fy = int(cluster_y + distance * math.sin(angle))

            # Clamp to world bounds
            fx = max(0, min(self.width - 1, fx))
            fy = max(0, min(self.height - 1, fy))

            # Check if position is available
            if (fx, fy) not in occupied_positions and (fx, fy) not in food_positions:
                return Food(x=fx, y=fy, energy=FOOD_ENERGY)

        # Could not find valid position near this cluster
        return None

    def maybe_move_clusters(self) -> None:
        """Occasionally move cluster centers to create dynamic niches."""
        if self.generation > 0 and self.generation % CLUSTER_MOVE_INTERVAL == 0:
            # Move one random cluster to a new location
            if self.food_clusters:
                idx = random.randint(0, len(self.food_clusters) - 1)
                new_x = random.randint(0, self.width - 1)
                new_y = random.randint(0, self.height - 1)
                self.food_clusters[idx] = (new_x, new_y)

    def get_food_spawn_rate(self) -> float:
        """
        Calculate dynamic food spawn rate based on temporal variation.
        Uses seasonal cycles to create boom-bust dynamics.
        """
        if not ENABLE_TEMPORAL_VARIATION:
            return float(FOOD_SPAWN_PER_TURN)

        # Calculate phase in seasonal cycle (0.0 to 1.0)
        phase = (self.generation % SEASON_CYCLE_LENGTH) / SEASON_CYCLE_LENGTH

        # Sine wave oscillation between min and max spawn rates
        # Peak at phase=0.25 (abundance), trough at phase=0.75 (scarcity)
        base_rate = (SEASON_MIN_SPAWN_RATE + SEASON_MAX_SPAWN_RATE) / 2.0
        amplitude = (SEASON_MAX_SPAWN_RATE - SEASON_MIN_SPAWN_RATE) / 2.0
        spawn_rate = base_rate + amplitude * math.sin(2 * math.pi * phase)

        return spawn_rate

    def next_step(self) -> "EvolutionWorld":
        """
        Advance the simulation by one step.
        1. Decide actions for all creatures
        2. Process reproduction
        3. Process movement and energy consumption
        4. Process food consumption
        5. Apply metabolism costs
        6. Age creatures
        7. Remove dead creatures
        8. Remove eaten food
        9. Spawn new food
        """
        new_creatures = []
        new_foods = list(self.foods)  # Copy food list
        eaten_food_positions = set()
        next_id = self.next_creature_id

        # Step 1: Decide actions for all creatures
        creature_actions = []
        for creature in self.creatures:
            action = behaviors.decide_action(creature, self)
            creature_actions.append((creature, action))

        # Step 2 & 3: Process actions (reproduction and movement)
        # Track positions occupied by creatures during this turn to prevent collisions
        occupied_this_turn: set[tuple[int, int]] = set()

        for creature, action in creature_actions:
            dx, dy = action

            # Check for reproduction signal
            if dx == -1 and dy == -1:
                # Try to reproduce
                empty_neighbor = behaviors.find_empty_neighbor(
                    creature.x, creature.y, self
                )
                # Check if empty_neighbor is not occupied by a creature that moved this turn
                if empty_neighbor and empty_neighbor not in occupied_this_turn:
                    # Perform reproduction
                    parent_after, child = creature.reproduce(next_id)
                    next_id += 1
                    # Place child at empty neighbor
                    child = child.move_to(empty_neighbor[0], empty_neighbor[1])
                    # Mark both positions as occupied
                    occupied_this_turn.add((creature.x, creature.y))
                    occupied_this_turn.add(empty_neighbor)
                    new_creatures.append(parent_after)
                    new_creatures.append(child)
                else:
                    # No space to reproduce, just keep the creature in its position
                    occupied_this_turn.add((creature.x, creature.y))
                    new_creatures.append(creature)
            else:
                # Movement - move up to 'speed' steps in the same direction
                current_x, current_y = creature.x, creature.y
                steps_moved = 0

                # Check if we're actually trying to move
                if dx != 0 or dy != 0:
                    # Try to move 'speed' times in the same direction
                    for _ in range(creature.genes.speed):
                        new_x = current_x + dx
                        new_y = current_y + dy

                        # Check if destination is valid and not occupied this turn
                        if (
                            new_x,
                            new_y,
                        ) in occupied_this_turn or not self.is_valid_position(
                            new_x, new_y
                        ):
                            # Can't move further, stop here
                            break

                        # Move to the new position
                        current_x, current_y = new_x, new_y
                        steps_moved += 1

                    # Update creature position if we moved
                    if steps_moved > 0:
                        creature = creature.move_to(current_x, current_y)
                        occupied_this_turn.add((current_x, current_y))

                        # Charge energy cost based on speed (not actual steps for consistent selection pressure)
                        energy_cost = creature.genes.move_cost * creature.genes.speed
                        creature = creature.model_copy(
                            update={"energy": max(0, creature.energy - energy_cost)}
                        )
                    else:
                        # Couldn't move at all, stay in current position
                        occupied_this_turn.add((creature.x, creature.y))
                else:
                    # Staying still
                    occupied_this_turn.add((creature.x, creature.y))

                new_creatures.append(creature)

        # Step 4: Process food consumption
        creatures_after_eating = []
        for creature in new_creatures:
            # Check if there's food at this position
            food_at_position = None
            for food in new_foods:
                if food.x == creature.x and food.y == creature.y:
                    food_at_position = food
                    break

            if food_at_position:
                # Eat the food
                creature = creature.eat(food_at_position.energy)
                eaten_food_positions.add((food_at_position.x, food_at_position.y))

            creatures_after_eating.append(creature)

        # Step 5 & 6: Apply metabolism and age
        creatures_after_metabolism = []
        for creature in creatures_after_eating:
            creature = creature.consume_metabolism()
            creature = creature.age_one_turn()
            creatures_after_metabolism.append(creature)

        # Step 7: Remove dead creatures
        alive_creatures = [c for c in creatures_after_metabolism if c.is_alive()]

        # Step 8: Remove eaten food
        remaining_foods = [
            f for f in new_foods if (f.x, f.y) not in eaten_food_positions
        ]

        # Step 9: Move cluster centers occasionally (dynamic niches)
        self.maybe_move_clusters()

        # Step 10: Spawn new food in clusters (spatial heterogeneity + temporal variation)
        current_food_count = len(remaining_foods)
        foods_to_spawn = int(self.get_food_spawn_rate())

        # Don't exceed MAX_FOOD
        if current_food_count < MAX_FOOD:
            foods_to_spawn = min(foods_to_spawn, MAX_FOOD - current_food_count)

            # Build sets for efficient position checking
            occupied_positions = {(c.x, c.y) for c in alive_creatures}
            food_positions = {(f.x, f.y) for f in remaining_foods}

            for _ in range(foods_to_spawn):
                # Spawn food near a cluster
                new_food = self.spawn_food_near_cluster(
                    occupied_positions, food_positions
                )
                if new_food:
                    remaining_foods.append(new_food)
                    food_positions.add((new_food.x, new_food.y))

        # Return new world state
        return EvolutionWorld(
            width=self.width,
            height=self.height,
            creatures=alive_creatures,
            foods=remaining_foods,
            generation=self.generation + 1,
            next_creature_id=next_id,
            food_clusters=self.food_clusters,
        )
