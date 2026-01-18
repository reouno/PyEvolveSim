"""Configuration parameters for the evolution simulation."""

# World dimensions
WORLD_WIDTH = 90
WORLD_HEIGHT = 35

# Initial population
INITIAL_CREATURES = 20  # Increased for larger world
MAX_FOOD = (
    100  # Maximum food items that can exist in the world (scaled with world size)
)

# Energy system
FOOD_ENERGY = 60  # Increased from 50 (20% increase)
INITIAL_ENERGY = 60  # Increased from 50 (20% increase)

# Food spawning - fixed rate per turn (creates resource scarcity)
FOOD_SPAWN_PER_TURN = 3  # Balanced resource rate for larger world (scaled from 2)

# Food clustering parameters (Phase 1.1: Environmental Heterogeneity)
NUM_FOOD_CLUSTERS = (
    6  # Number of cluster centers in the world (doubled for larger space)
)
CLUSTER_SPREAD = (
    0.25  # Controls how tightly food clusters (slightly wider spread for larger world)
)
CLUSTER_MOVE_INTERVAL = 50  # Generations between cluster movements

# Temporal variation parameters (Phase 1.2: Dynamic Resource Availability)
ENABLE_TEMPORAL_VARIATION = True  # Toggle seasonal food cycles
SEASON_CYCLE_LENGTH = 100  # Generations per seasonal cycle
SEASON_MIN_SPAWN_RATE = 1.5  # Minimum food spawn rate (increased to prevent extinction)
SEASON_MAX_SPAWN_RATE = 3.5  # Maximum food spawn rate (abundance)

# Default gene values
DEFAULT_MOVE_COST = 0.9  # Reduced from 1.0 (10% reduction)
DEFAULT_VISION_RANGE = 3
DEFAULT_REPRODUCTION_THRESHOLD = 100.0  # Requires ~1.67 food items to reproduce
DEFAULT_METABOLISM = 1.2  # Balanced cost for sustainable population
DEFAULT_SPEED = 1  # 1-3 cells per turn
DEFAULT_MAX_ENERGY = 200.0  # Phase 2.1: Energy capacity (100-300 range)
DEFAULT_FOOD_EFFICIENCY = 1.0  # Phase 2.2: Food energy absorption (0.7-1.3 range)
# Energy balance (with new constraints):
#   Food: 2-3/turn × 60 = 120-180 energy/turn
#   Min cost/creature: 0.5 (move) + 0.8 (metab) = 1.3 energy/turn
#   Max sustainable: 180 ÷ 1.3 ≈ 138 creatures
#   Target range: 60-100 creatures (balanced population)

# Reproduction parameters
MIN_REPRODUCTION_AGE = 5  # Creatures must be this many turns old to reproduce

# Mutation parameters (Phase 3: Stronger evolution)
MUTATION_RATE = 0.3  # 30% chance of mutation for faster evolution
MUTATION_STRENGTH = 0.20  # ±20% variation (reduced from 0.25 for better stability)
LARGE_MUTATION_CHANCE = 0.08  # 8% chance of large mutation (reduced from 0.1)
LARGE_MUTATION_STRENGTH = 0.5  # ±50% variation for large jumps

# Simulation parameters
DEFAULT_DELAY = 0.2  # seconds between updates

# Graph parameters
ENABLE_GRAPH = True  # Toggle graph display
GRAPH_RECORD_INTERVAL = 10  # Record stats every N generations
GRAPH_HEIGHT = 10  # Height of graph area in lines
GRAPH_MAX_POINTS = (
    80  # Maximum number of points to display (increased for larger world)
)
