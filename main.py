from life_game.game import Game
from life_game.patterns import (
    GLIDER,
    BLINKER,
    PULSAR,
    GOSPER_GLIDER_GUN,
    create_random_grid,
    create_grid_with_pattern,
)


def run_conway_life():
    """Run Conway's Game of Life."""
    print("Conway's Game of Life")
    print("=" * 50)
    print("\nAvailable patterns:")
    print("1. Random")
    print("2. Glider")
    print("3. Blinker")
    print("4. Pulsar")
    print("5. Gosper Glider Gun")
    print()

    choice = input("Select a pattern (1-5, default: 1): ").strip() or "1"

    # Grid dimensions
    width = 50
    height = 20

    if choice == "1":
        grid = create_random_grid(width, height, density=0.3)
    elif choice == "2":
        grid = create_grid_with_pattern(width, height, GLIDER, center=True)
    elif choice == "3":
        grid = create_grid_with_pattern(width, height, BLINKER, center=True)
    elif choice == "4":
        grid = create_grid_with_pattern(width, height, PULSAR, center=True)
    elif choice == "5":
        grid = create_grid_with_pattern(width, height, GOSPER_GLIDER_GUN, center=True)
    else:
        print("Invalid choice, using random pattern.")
        grid = create_random_grid(width, height, density=0.3)

    print("\nStarting game... Press Ctrl+C to exit.\n")

    game = Game(grid=grid, delay=0.1)
    game.run()


def run_evolution_simulation():
    """Run the evolution simulation."""
    import random
    from life_game.evolution.simulation import EvolutionSimulation
    from life_game.evolution.world import EvolutionWorld
    from life_game.evolution.creature import Creature, Genes
    from life_game.evolution.config import (
        WORLD_WIDTH,
        WORLD_HEIGHT,
        INITIAL_CREATURES,
        MAX_FOOD,
        INITIAL_ENERGY,
        DEFAULT_DELAY,
    )

    print("Evolution Simulation (エネルギーベース進化)")
    print("=" * 50)
    print("\nInitializing world...")

    # Create initial creatures
    creatures = []
    for i in range(INITIAL_CREATURES):
        creatures.append(
            Creature(
                x=random.randint(0, WORLD_WIDTH - 1),
                y=random.randint(0, WORLD_HEIGHT - 1),
                energy=INITIAL_ENERGY,
                genes=Genes(),
                id=i,
            )
        )

    # Create world (food will be added after cluster initialization)
    world = EvolutionWorld(
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        creatures=creatures,
        foods=[],
        next_creature_id=INITIAL_CREATURES,
    )

    # Initialize food clusters for spatial heterogeneity
    world.initialize_food_clusters()

    # Create initial food near clusters
    foods = []
    occupied_positions = {(c.x, c.y) for c in creatures}
    food_positions: set[tuple[int, int]] = set()

    for _ in range(MAX_FOOD):
        new_food = world.spawn_food_near_cluster(occupied_positions, food_positions)
        if new_food:
            foods.append(new_food)
            food_positions.add((new_food.x, new_food.y))

    world.foods = foods

    print(f"Created {len(creatures)} creatures and {len(foods)} food items.")
    print("\nStarting simulation... Press Ctrl+C to exit.\n")

    # Run simulation
    sim = EvolutionSimulation(world=world, delay=DEFAULT_DELAY)
    sim.run()


def main():
    """Main entry point for the simulation selector."""
    print("Select simulation:")
    print("1. Conway's Game of Life")
    print("2. Evolution Simulation (エネルギーベース進化)")
    print()

    choice = input("Select (1-2, default: 1): ").strip() or "1"

    if choice == "2":
        run_evolution_simulation()
    else:
        run_conway_life()


if __name__ == "__main__":
    main()
