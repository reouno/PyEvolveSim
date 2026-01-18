"""Creature and Genes classes for the evolution simulation."""

from pydantic import BaseModel, Field

from .config import (
    DEFAULT_MOVE_COST,
    DEFAULT_VISION_RANGE,
    DEFAULT_REPRODUCTION_THRESHOLD,
    DEFAULT_METABOLISM,
    DEFAULT_SPEED,
    DEFAULT_MAX_ENERGY,
    DEFAULT_FOOD_EFFICIENCY,
    MUTATION_RATE,
    MUTATION_STRENGTH,
    LARGE_MUTATION_CHANCE,
    LARGE_MUTATION_STRENGTH,
)
from .mutation import mutate_gene_value


class Genes(BaseModel):
    """Genetic traits that can be inherited and mutated."""

    move_cost: float = Field(default=DEFAULT_MOVE_COST, ge=0.5, le=2.0)
    vision_range: int = Field(default=DEFAULT_VISION_RANGE, ge=1, le=10)
    reproduction_threshold: float = Field(
        default=DEFAULT_REPRODUCTION_THRESHOLD, ge=10.0
    )
    metabolism: float = Field(default=DEFAULT_METABOLISM, ge=0.8, le=2.0)
    speed: int = Field(default=DEFAULT_SPEED, ge=1, le=3)
    max_energy: float = Field(default=DEFAULT_MAX_ENERGY, ge=100.0, le=300.0)
    food_efficiency: float = Field(default=DEFAULT_FOOD_EFFICIENCY, ge=0.7, le=1.3)

    def mutate(self) -> "Genes":
        """
        Return a new Genes instance with potential mutations.
        Uses the mutation module to ensure values stay within valid ranges.
        """
        new_genes: dict[str, float | int] = {}

        for field_name, value in self.model_dump().items():
            new_value = mutate_gene_value(
                field_name=field_name,
                current_value=value,
                mutation_rate=MUTATION_RATE,
                mutation_strength=MUTATION_STRENGTH,
                large_mutation_strength=LARGE_MUTATION_STRENGTH,
                large_mutation_chance=LARGE_MUTATION_CHANCE,
            )
            new_genes[field_name] = new_value

        # Pydantic will validate types at runtime
        return Genes(**new_genes)  # type: ignore[arg-type]


class Creature(BaseModel):
    """A creature with position, energy, and genetic traits."""

    x: int
    y: int
    energy: float = Field(ge=0)
    genes: Genes
    age: int = Field(default=0, ge=0)
    generation: int = Field(default=0, ge=0)
    id: int

    def move_to(self, new_x: int, new_y: int) -> "Creature":
        """Return a new Creature at the specified position."""
        return self.model_copy(update={"x": new_x, "y": new_y})

    def consume_metabolism(self) -> "Creature":
        """Return a new Creature with energy reduced by metabolism cost."""
        new_energy = max(0, self.energy - self.genes.metabolism)
        return self.model_copy(update={"energy": new_energy})

    def consume_move_cost(self) -> "Creature":
        """Return a new Creature with energy reduced by movement cost."""
        new_energy = max(0, self.energy - self.genes.move_cost)
        return self.model_copy(update={"energy": new_energy})

    def eat(self, food_energy: float) -> "Creature":
        """
        Return a new Creature with energy increased by food (capped at max_energy).
        Food efficiency determines how much energy is absorbed from food.
        """
        absorbed_energy = food_energy * self.genes.food_efficiency
        new_energy = min(self.energy + absorbed_energy, self.genes.max_energy)
        return self.model_copy(update={"energy": new_energy})

    def reproduce(self, child_id: int) -> tuple["Creature", "Creature"]:
        """
        Return a tuple of (parent_after_reproduction, child).
        Parent and child split energy 50-50 to create equal opportunity.
        Selection pressure comes from resource scarcity, not reproduction cost.
        """
        parent_energy = self.energy * 0.5
        child_energy = self.energy * 0.5
        child_genes = self.genes.mutate()

        parent_after = self.model_copy(update={"energy": parent_energy})
        child = Creature(
            x=self.x,
            y=self.y,
            energy=child_energy,
            genes=child_genes,
            age=0,
            generation=self.generation + 1,
            id=child_id,
        )

        return parent_after, child

    def age_one_turn(self) -> "Creature":
        """Return a new Creature with age incremented by 1."""
        return self.model_copy(update={"age": self.age + 1})

    def is_alive(self) -> bool:
        """Check if the creature has enough energy to survive."""
        return self.energy > 0
