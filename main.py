from life_game.game import Game
from life_game.patterns import (
    GLIDER,
    BLINKER,
    PULSAR,
    GOSPER_GLIDER_GUN,
    create_random_grid,
    create_grid_with_pattern,
)


def main():
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


if __name__ == "__main__":
    main()
