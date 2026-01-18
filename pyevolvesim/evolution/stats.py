"""Statistics calculation for the evolution simulation."""

import math
from pydantic import BaseModel

from .world import EvolutionWorld


class WorldStats(BaseModel):
    """Statistics about the current world state."""

    generation: int
    creature_count: int
    food_count: int
    avg_energy: float
    avg_age: float
    avg_move_cost: float
    avg_vision_range: float
    avg_reproduction_threshold: float
    avg_metabolism: float
    avg_speed: float
    avg_max_energy: float
    avg_food_efficiency: float
    # Diversity metrics (standard deviations)
    std_speed: float
    std_vision_range: float
    std_move_cost: float
    std_metabolism: float
    std_max_energy: float
    std_food_efficiency: float
    # Current food spawn rate (for temporal variation visibility)
    current_food_spawn_rate: float

    @classmethod
    def from_world(cls, world: EvolutionWorld) -> "WorldStats":
        """Calculate statistics from a world state."""
        creature_count = len(world.creatures)
        food_count = len(world.foods)

        if creature_count == 0:
            # No creatures, return zeros for averages
            return cls(
                generation=world.generation,
                creature_count=0,
                food_count=food_count,
                avg_energy=0.0,
                avg_age=0.0,
                avg_move_cost=0.0,
                avg_vision_range=0.0,
                avg_reproduction_threshold=0.0,
                avg_metabolism=0.0,
                avg_speed=0.0,
                avg_max_energy=0.0,
                avg_food_efficiency=0.0,
                std_speed=0.0,
                std_vision_range=0.0,
                std_move_cost=0.0,
                std_metabolism=0.0,
                std_max_energy=0.0,
                std_food_efficiency=0.0,
                current_food_spawn_rate=world.get_food_spawn_rate(),
            )

        # Calculate averages
        total_energy = sum(c.energy for c in world.creatures)
        total_age = sum(c.age for c in world.creatures)
        total_move_cost = sum(c.genes.move_cost for c in world.creatures)
        total_vision_range = sum(c.genes.vision_range for c in world.creatures)
        total_reproduction_threshold = sum(
            c.genes.reproduction_threshold for c in world.creatures
        )
        total_metabolism = sum(c.genes.metabolism for c in world.creatures)
        total_speed = sum(c.genes.speed for c in world.creatures)
        total_max_energy = sum(c.genes.max_energy for c in world.creatures)
        total_food_efficiency = sum(c.genes.food_efficiency for c in world.creatures)

        avg_move_cost = total_move_cost / creature_count
        avg_vision_range = total_vision_range / creature_count
        avg_metabolism = total_metabolism / creature_count
        avg_speed = total_speed / creature_count
        avg_max_energy = total_max_energy / creature_count
        avg_food_efficiency = total_food_efficiency / creature_count

        # Calculate standard deviations (diversity metrics)
        def std_dev(values: list[float], mean: float) -> float:
            if len(values) <= 1:
                return 0.0
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            return math.sqrt(variance)

        speeds = [float(c.genes.speed) for c in world.creatures]
        visions = [float(c.genes.vision_range) for c in world.creatures]
        move_costs = [c.genes.move_cost for c in world.creatures]
        metabolisms = [c.genes.metabolism for c in world.creatures]
        max_energies = [c.genes.max_energy for c in world.creatures]
        food_efficiencies = [c.genes.food_efficiency for c in world.creatures]

        return cls(
            generation=world.generation,
            creature_count=creature_count,
            food_count=food_count,
            avg_energy=total_energy / creature_count,
            avg_age=total_age / creature_count,
            avg_move_cost=avg_move_cost,
            avg_vision_range=avg_vision_range,
            avg_reproduction_threshold=total_reproduction_threshold / creature_count,
            avg_metabolism=avg_metabolism,
            avg_speed=avg_speed,
            avg_max_energy=avg_max_energy,
            avg_food_efficiency=avg_food_efficiency,
            std_speed=std_dev(speeds, avg_speed),
            std_vision_range=std_dev(visions, avg_vision_range),
            std_move_cost=std_dev(move_costs, avg_move_cost),
            std_metabolism=std_dev(metabolisms, avg_metabolism),
            std_max_energy=std_dev(max_energies, avg_max_energy),
            std_food_efficiency=std_dev(food_efficiencies, avg_food_efficiency),
            current_food_spawn_rate=world.get_food_spawn_rate(),
        )
