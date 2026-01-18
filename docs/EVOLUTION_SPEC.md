# Evolution Simulation Specification

## Overview

This document specifies the current design, known limitations, and proposed improvements for the Evolution Simulation. It focuses on **what** the system does and **why**, rather than implementation details.

**Purpose:**
1. Document current system specifications
2. Identify known limitations and issues
3. Propose concrete improvements
4. Outline future extension directions

---

## Part 1: Current Specifications

### 1.1 Architecture Overview

The evolution simulation consists of 11 modules with distinct responsibilities:

| Module | Responsibility | Characteristics |
|--------|----------------|-----------------|
| `config.py` | Configuration parameters | Manages 68 settings |
| `creature.py` | Creature/Genes models | Type-safe validation with Pydantic |
| `food.py` | Food model | Energy-bearing resources |
| `world.py` | World state management | Immutable state transitions |
| `behaviors.py` | Behavior decision logic | Pure functions |
| `mutation.py` | Mutation logic | Pure functions, testable |
| `stats.py` | Statistics calculation | Averages and standard deviations |
| `stats_history.py` | Statistics history | Data collection for graphs |
| `graph_renderer.py` | Graph rendering | Terminal-based visualization |
| `renderer.py` | Main rendering | Integrated display |
| `simulation.py` | Simulation execution | Main loop and user input |

**Design Principles:**
- **Separation of Concerns**: Each module has a single responsibility
- **Loose Coupling**: Protocol-based interfaces
- **Type Safety**: Complete type checking with mypy
- **Testability**: 71 tests providing coverage
- **Immutability**: State changes return new instances

### 1.2 Core Mechanics

#### Energy System

**Energy Balance:**
- Food energy per item: 60
- Initial creature energy: 60
- Food spawn per turn: 3 (base rate)
- Maximum food in world: 100

**Energy Consumption:**
- **Metabolism cost**: Consumed every turn (default: 1.2)
- **Movement cost**: speed × move_cost (default: 1 × 0.9 = 0.9)
- **Minimum total**: 1.3 energy/turn
- **Maximum total**: 4.0 energy/turn

**Energy Acquisition:**
- Eating food provides: FOOD_ENERGY × food_efficiency
- Cannot exceed max_energy capacity
- Absorption efficiency determined by food_efficiency gene (0.7-1.3)

**Death Condition:**
- Energy reaches 0 → creature dies

#### Reproduction System

**Reproduction Conditions:**
```
threshold = max_energy × 0.6  # 60% of maximum energy
can_reproduce = (energy >= threshold) and (age >= 5 turns)
```

**Reproduction Mechanics:**
1. Parent's energy split 50:50 between parent and offspring
2. Offspring inherits parent's genes with mutations applied
3. Offspring placed in adjacent cell (4 directions: up/down/left/right)
4. If all adjacent cells occupied, reproduction **silently fails** (known issue)
5. Generation counter increments by 1

**r/K Strategy:**
- Small max_energy → reproduce quickly (r-strategy)
- Large max_energy → survive starvation (K-strategy)

#### Movement System

**Decision Priority:**
1. Reproduce if conditions met
2. Move toward nearest visible food
3. Random movement

**Current Limitations:**
- **4 directions only**: No diagonal movement
- **Greedy pathfinding**: Moves directly toward target, no obstacle avoidance
- **Vision range**: Detects food within Manhattan distance defined by vision_range gene (1-10)
- **Speed**: Can move multiple cells per turn based on speed gene (1-3)

### 1.3 Genetic System

Seven genetic traits are implemented:

| Gene | Range | Default | Purpose |
|------|-------|---------|---------|
| `move_cost` | 0.5 - 2.0 | 0.9 | Energy cost per cell moved |
| `vision_range` | 1 - 10 | 3 | Food detection range (Manhattan distance) |
| `reproduction_threshold` | 10.0 - ∞ | 100.0 | **Note:** Currently unused (replaced by max_energy × 0.6) |
| `metabolism` | 0.8 - 2.0 | 1.2 | Baseline metabolism cost per turn |
| `speed` | 1 - 3 | 1 | Cells moved per turn |
| `max_energy` | 100.0 - 300.0 | 200.0 | Maximum energy capacity (determines r/K strategy) |
| `food_efficiency` | 0.7 - 1.3 | 1.0 | Energy absorption efficiency from food |

**Mutation Mechanics:**
- **Mutation rate**: 30% (each gene has 30% chance to mutate)
- **Normal mutations**: ±20% variation
- **Large mutations**: 8% chance of ±50% variation
- **Integer genes**: Rounded and clamped to constraints after mutation
- **Continuous genes**: Clamped to range after mutation

### 1.4 Environmental Systems

#### Food Clustering (Spatial Heterogeneity)

**Configuration:**
- Number of cluster centers: 6
- Cluster spread: 0.25 (exponential distribution)
- Cluster movement interval: Every 50 generations

**Mechanism:**
1. Random cluster centers placed at initialization
2. Food spawns near randomly selected cluster center
3. Distance from center determined by exponential distribution
4. One cluster center moves randomly every 50 generations

**Effect:**
- Food distributed unevenly, creating spatial niches
- Fast creatures → advantage in dense areas (win competition)
- Efficient creatures → advantage in sparse areas (endure travel costs)

#### Temporal Variation (Boom-Bust Cycles)

**Configuration:**
- Enable/disable toggle available
- Cycle length: 100 generations
- Minimum spawn rate: 1.5 (scarcity phase)
- Maximum spawn rate: 3.5 (abundance phase)

**Formula:**
```
phase = (generation % CYCLE_LENGTH) / CYCLE_LENGTH
base_rate = (MIN + MAX) / 2.0
amplitude = (MAX - MIN) / 2.0
spawn_rate = base_rate + amplitude × sin(2π × phase)
```

**Effect:**
- Food spawn rate varies sinusoidally
- Abundance phase (phase=0.25): r-strategists thrive
- Scarcity phase (phase=0.75): K-strategists thrive
- Prevents single strategy from dominating

### 1.5 Statistics & Visualization

**Statistics Tracked:**
- Population counts (creatures, food)
- Average traits (speed, vision, move_cost, metabolism, max_energy, food_efficiency)
- Diversity metrics (standard deviation of all traits)

**Graph Display:**
- Terminal-based ASCII graphs
- Maximum 80 data points displayed
- Records every 10 generations
- Shows: population trends, average speed, diversity trends

---

## Part 2: Known Limitations & Issues

### 2.1 Movement System Issues

#### Issue 1: 4-Direction Movement Only

**Problem:**
- Diagonal movement unavailable
- Reaching diagonal food requires detour
- Manhattan distance 3 diagonal position takes 6 turns (should be 3)
- Movement efficiency reduced, energy wasted

#### Issue 2: Greedy Pathfinding Limitations

**Problem:**
- Cannot navigate around obstacles
- Gets stuck when surrounded by walls or creatures
- No route planning, only immediate local decisions

**Example scenario:**
```
Creature approaches food but blocked by wall
Current behavior: Stops moving (stuck)
Desired behavior: Find alternate route around obstacle
```

#### Issue 3: No Advanced Pathfinding

**Missing features:**
- A* algorithm for shortest path
- Dijkstra algorithm
- Obstacle avoidance strategies
- Path caching

### 2.2 Reproduction System Limitations

#### Issue 1: Silent Reproduction Failure

**Problem:**
- Reproduction fails without logging when adjacent cells full
- No debugging information available
- Statistics don't track failure rate
- Cannot diagnose why population becomes unstable

#### Issue 2: Adjacent-Cell-Only Placement

**Problem:**
- Only checks 4 adjacent cells for offspring placement
- Dense areas make reproduction extremely difficult
- Creatures with reproduction energy cannot reproduce due to lack of space
- r-strategists lose their advantage in crowded areas

**Proposed improvement:**
- Expand search radius to 2-3 cells
- Prioritize closer positions

#### Issue 3: Lack of Reproduction Feedback

**User perspective:**
- Cannot tell if reproduction succeeded
- Cannot determine if failure rate is high
- Insufficient data for tuning parameters

### 2.3 Population Stability Issues

#### Issue 1: Extinction Risk

**Phenomenon:**
- Inappropriate initial parameters cause extinction within few generations
- Population crashes rapidly during food scarcity periods
- No recovery mechanism

**Causes:**
- Fixed food spawn rate may be insufficient
- High metabolism/movement costs can make population unsustainable
- Vulnerable with small initial population

#### Issue 2: No Carrying Capacity

**Current state:**
- Only MAX_FOOD limit (100)
- No creature population limit
- High density → intense food competition → rapid population collapse

**Problem:**
- No soft carrying capacity (density-dependent mortality)
- Population explodes then crashes
- Difficult to maintain stable population

#### Issue 3: No Recovery Mechanism

**Current behavior:**
- Food spawn rate unchanged even when population drops below 10
- Few creatures in large world → inefficient food finding
- No recovery opportunity → extinction

**Desired behavior:**
- Increase food spawn rate when population low
- Temporarily reduce metabolism costs (environmental improvement)
- Minimum population guarantee (research mode)

### 2.4 Behavioral Diversity Issues

#### Issue 1: Single Decision Algorithm

**Problem:**
- All creatures use identical decision logic
- Exploration vs. exploitation trade-off doesn't evolve genetically
- No behavioral diversity emerges

#### Issue 2: No Exploration Tendency Gene

**Missing functionality:**
- Random movement frequency gene
- Probability to explore even when food visible
- Risk aversion vs. risk preference personality

**Impact:**
- All creatures always target nearest food
- Local competition intensifies
- New food source discovery left to chance

#### Issue 3: Missing Genes for Future Extensions

**Currently absent:**
- `exploration_tendency`: Exploration tendency (0.0-1.0)
- `aggression`: Aggression for future predator features
- `cooperation`: Cooperation for future social behaviors
- `memory_capacity`: Memory capacity for food location recall

### 2.5 Collision & Concurrency Issues

#### Issue 1: Sequential Processing Dependency

**Problem:**
- Creatures processed sequentially, not simultaneously
- Two creatures moving to same cell → first processed wins
- Lacks fairness

**Example:**
```
Creature A at (0,0) → wants (1,0)
Creature B at (2,0) → wants (1,0)

Current: A processed first → A succeeds, B fails
Desired: Detect conflict → resolve (random, energy-based, speed-based)
```

#### Issue 2: Turn-Based System Strictness

**Current implementation:**
- Decide all actions (step 1)
- Execute sequentially (steps 2-3)

**Ideal implementation:**
- Decide all actions
- Check for conflicts
- Resolve with priority queue
- Execute simultaneously

### 2.6 Gene Redundancy

#### Issue: max_energy vs. food_efficiency Overlap

**Concern:**
- Large max_energy → high energy storage → starvation resistant
- Large food_efficiency → more energy per food → starvation resistant

Both provide similar benefits, potentially reducing diversity if only one optimizes.

**Verification needed:**
- Check if both genes evolve independently in simulation
- If highly correlated, consider consolidation or differentiation

---

## Part 3: Proposed Improvements

### 3.1 Movement System Improvements

#### Improvement 1: 8-Direction Movement

**Change:**
- Add diagonal movement (8 directions total)
- Apply √2 cost multiplier for diagonal moves

**Benefits:**
- More intuitive movement
- Faster food acquisition
- Improved movement efficiency

**Trade-offs:**
- Diagonal movement might be too advantageous (address with cost adjustment)

#### Improvement 2: A* Pathfinding

**Specification:**
- Implement A* algorithm for shortest path finding
- Use for creatures with high vision_range (≥5)
- Fallback to greedy pathfinding for low vision
- Make configurable (greedy/astar/dijkstra options)

**Benefits:**
- Obstacle avoidance
- Shortest path discovery
- Smarter high-vision creatures

**Trade-offs:**
- Higher computational cost
- More complex implementation

### 3.2 Reproduction System Enhancements

#### Improvement 1: Reproduction Failure Logging

**Specification:**
- Add reproduction_attempts, reproduction_successes, reproduction_failures to statistics
- Calculate reproduction_success_rate
- Optional debug logging for failures
- Display in UI

**Benefits:**
- Better debugging
- Tuning insights
- Visibility into system behavior

#### Improvement 2: Extended Offspring Placement Search

**Specification:**
- Search within configurable radius (default: 2 cells)
- Prioritize closer positions
- Shuffle positions at same distance for fairness

**Benefits:**
- Reproduction possible in dense areas
- r-strategists retain advantage
- Faster population recovery

#### Improvement 3: Reproduction Energy Investment Gene (Future)

**Specification:**
- New gene: reproduction_investment (0.3-0.7, default: 0.5)
- 0.3 = parent keeps 70%, offspring gets 30% (selfish)
- 0.5 = 50:50 split (current)
- 0.7 = parent keeps 30%, offspring gets 70% (altruistic)

**Effects:**
- Selfish strategy: Parent survives longer, multiple reproductions
- Altruistic strategy: Offspring starts with more energy, higher survival

### 3.3 Population Stability Improvements

#### Improvement 1: Soft Carrying Capacity

**Specification:**
- Target population: 80 creatures
- Death probability increases with population above target
- Death probability = min(0.5, excess × 0.02)

**Benefits:**
- Prevents population explosion
- Represents environmental resource limits
- More realistic ecosystem simulation

#### Improvement 2: Minimum Population Protection

**Specification:**
- Enable/disable toggle
- Threshold: 10 creatures
- Recovery mode: Food spawn rate × 2.0 when below threshold

**Benefits:**
- Prevents extinction
- Enables longer runs
- More tuning opportunities

**Trade-offs:**
- Natural selection incomplete
- Need research mode vs. realistic mode toggle

#### Improvement 3: Adaptive Metabolism

**Specification:**
- Metabolism cost adjusted by environmental stress level
- Stress level based on food availability per creature
- Stress factor: 0.8 (20% reduction during easy times)

**Benefits:**
- Represents environmental variability
- Helps population recovery
- More dynamic ecosystem

### 3.4 Behavioral Diversity Additions

#### Improvement 1: Exploration Tendency Gene

**Specification:**
- New gene: exploration_tendency (0.0-1.0, default: 0.5)
- 0.0 = fully exploitative (always go to food)
- 1.0 = fully explorative (always random movement)
- Probabilistic choice between exploitation and exploration

**Effects:**
- High exploration: Discovers new food sources, avoids competition
- Low exploration: Secures visible food, must win competition

**Evolution pressure:**
- Dense food distribution → low exploration advantaged
- Sparse food distribution → high exploration advantaged

#### Improvement 2: Future Predator Genes

**Specification:**
- aggression gene (0.0-1.0) for future predator features
- Currently unused but defined for future compatibility

#### Improvement 3: Social Behavior Genes

**Specification:**
- cooperation gene (0.0-1.0) for future herd/sharing behaviors
- Currently unused but defined for future compatibility

### 3.5 Collision Handling Improvements

**Specification:**
- Priority-based processing: speed + random tiebreaker
- Sort planned actions by priority
- Process in order with conflict resolution
- Faster creatures get priority (evolutionary pressure)

**Benefits:**
- Speed gene provides competitive advantage
- Fairer conflict resolution
- Reduces concurrency issues

### 3.6 Gene Redundancy Verification

**Specification:**
- Statistical analysis tool to check gene correlations
- Pearson correlation coefficient calculation
- Warning if correlation > 0.7

**If redundancy confirmed:**
- Option A: Clarify gene roles (max_energy for storage, food_efficiency for absorption)
- Option B: Consolidate genes, add new genes (e.g., memory_capacity)

---

## Part 4: Future Extensions

### Tier 1: Short-Term Extensions

Relatively easy to implement with minimal core system changes.

#### 4.1 Age-Dependent Traits

**Concept:** Trait modifiers based on creature age
- Young: Fast but inefficient
- Adult: Balanced
- Old: Slow but efficient

**Interest:** Adds life cycle complexity, generational turnover importance

#### 4.2 Day/Night Cycles

**Concept:** Time-of-day affects vision and food spawn
- Day: Wide vision, high food spawn
- Night: Narrow vision, low food spawn

**Interest:** Temporal niches, nocturnal vs. diurnal evolution

#### 4.3 Terrain Types

**Concept:** Different terrain types with varying movement costs and food availability
- Plains: Normal movement, normal food
- Forest: Slow movement, high food
- Water: Very slow movement, low food
- Mountain: Slow movement, low food

**Interest:** Spatial niche diversification, terrain adaptation

#### 4.4 Predator-Prey Dynamics

**Concept:** Carnivores hunt herbivores for energy
**Interest:** Trophic cascades, evolutionary arms races

**Complexity:** Medium (3-5 days)

#### 4.5 Sexual Reproduction

**Concept:** Reproduction requires two creatures, genes crossover from both parents
**Interest:** Genetic diversity, mate selection evolution

**Complexity:** Medium (3-4 days)

### Tier 2: Medium-Term Extensions

More complex, requiring system-wide changes.

#### 4.6 Social Behaviors

**Concept:** Herding, food sharing, communication
**Complexity:** High (7-10 days)

#### 4.7 Learning & Memory

**Concept:** Creatures remember food locations and visited areas
**Complexity:** High (5-7 days)

#### 4.8 Specialization

**Concept:** Herbivore, carnivore, omnivore, scavenger specializations
**Complexity:** Medium

#### 4.9 Diseases & Parasites

**Concept:** Infection spreads between creatures, immunity gene evolves
**Complexity:** Medium

#### 4.10 Migration Patterns

**Concept:** Seasonal movement, separation of breeding and feeding grounds
**Complexity:** Medium

### Tier 3: Long-Term Extensions

Require fundamental redesign.

#### 4.11 Multi-Species Ecosystem

**Concept:** Multiple independent species coexist, speciation simulation
**Complexity:** Very High

#### 4.12 Tool Use

**Concept:** Creatures create and use simple tools
**Complexity:** Very High

#### 4.13 Cultural Evolution

**Concept:** Behavioral transmission through learning, not genetics
**Complexity:** Very High

#### 4.14 Complex Environments

**Concept:** Caves, nests, territories; creatures modify environment
**Complexity:** Very High

#### 4.15 GUI Interface

**Concept:** Graphical UI replacing terminal display
**Technologies:** Pygame, PyQt/PySide, or Web (FastAPI + React)
**Complexity:** High

### Research-Level Ideas

#### 4.16 Neural Network Behaviors

**Concept:** Replace decision trees with evolved neural networks (NEAT algorithm)
**Complexity:** Very High (10-15 days)

#### 4.17 Genetic Programming

**Concept:** Evolve the behavior algorithm itself as code
**Complexity:** Very High

#### 4.18 Co-Evolution

**Concept:** Predators and prey mutually evolve, arms race simulation
**Requires:** Predator-prey system implementation first
**Complexity:** High

#### 4.19 Ecosystem Services

**Concept:** Pollination, decomposition, nutrient cycling in food web
**Complexity:** Very High

---

## Part 5: Implementation Priorities

### 5.1 Priority Matrix

| Category | Task | Priority | Complexity | Rationale |
|----------|------|----------|------------|-----------|
| **Fix** | 8-direction movement | **Critical** | Low | Dramatic efficiency improvement |
| **Fix** | Reproduction failure logging | **Critical** | Low | Essential for debugging/tuning |
| **Fix** | Population stabilization | **Critical** | Medium | Prevents extinction, enables long runs |
| **Fix** | Extended offspring placement | **High** | Low | Improves reproduction success rate |
| **Fix** | A* pathfinding | **High** | Medium | Smarter behavior, better UX |
| **Fix** | Exploration tendency gene | **High** | Low | First step toward behavioral diversity |
| **Fix** | Collision handling | **Medium** | Medium | Fairness improvement, not urgent |
| **Fix** | Gene redundancy check | **Medium** | Low | Statistical analysis only |
| **Extend** | Age-dependent traits | **Medium** | Low | Interesting dynamics, easy to implement |
| **Extend** | Day/night cycles | **Medium** | Low | Temporal niches, easy to implement |
| **Extend** | Terrain types | **Medium** | Medium | Spatial diversity, visual improvement |
| **Extend** | Predator-prey | **Low** | Medium | Interesting but increases complexity |
| **Extend** | Sexual reproduction | **Low** | Medium | Diversity improvement but not essential |
| **Extend** | Learning/memory | **Low** | High | Interesting but complex, can defer |
| **Extend** | Social behaviors | **Low** | High | Research-oriented, high complexity |
| **Extend** | Neural network | **Research** | Very High | Research project level |

### 5.2 Recommended Implementation Phases

#### Phase 1: Critical Fixes (1 week)

**Goal:** Stability and debuggability

1. Reproduction failure logging (0.5 days)
2. 8-direction movement (1-2 days)
3. Population stabilization (2-3 days)

**Outcome:** Stable simulation with long-term viability

#### Phase 2: Behavior Improvements (1 week)

**Goal:** Smarter, more diverse creatures

4. Extended offspring placement (1 day)
5. Exploration tendency gene (1-2 days)
6. A* pathfinding (3-4 days)

**Outcome:** Intelligent behavior and increased behavioral diversity

#### Phase 3: Environment Enrichment (1 week)

**Goal:** Richer environment, more niches

7. Age-dependent traits (1-2 days)
8. Day/night cycles (1-2 days)
9. Terrain types (2-4 days)

**Outcome:** Diversified environment with more ecological niches

#### Phase 4: Advanced Extensions (2-4 weeks)

**Goal:** Complex simulation features

10. Predator-prey (3-5 days)
11. Sexual reproduction (3-4 days)
12. Learning/memory (5-7 days)
13. Social behaviors (7-10 days)

**Outcome:** Research-level simulation

### 5.3 Quick Wins

Immediate implementation with high impact:

1. **Reproduction failure logging** (0.5 days) → Better debugging
2. **8-direction movement** (1-2 days) → Dramatic UX improvement
3. **Exploration tendency gene** (1-2 days) → Behavioral diversity
4. **Age-dependent traits** (1-2 days) → Visual interest

**Total: 5-7 days for major improvements**

### 5.4 Long-Term Vision

**Goal:** Educational and research tool for ecology and evolutionary biology

**Features:**
- Real-time parameter adjustment
- Data export (CSV, JSON)
- Evolution history visualization
- Phylogenetic tree display
- GUI interface

**Target Users:**
- Evolutionary biology students
- Ecology researchers
- Game developers (AI learning)
- Simulation enthusiasts

---

## Summary

This document specifies the evolution simulation's complete design, known limitations, proposed fixes, and future extension ideas.

**Next Steps:**
1. Begin Phase 1 (critical fixes) implementation
2. Run tests after each fix
3. Collect statistical data to verify effectiveness
4. Adjust priorities based on user feedback

**Project Goals:**
- Stable long-term simulation
- Coexistence of diverse ecological strategies
- Tool useful for education and research

---

**Document Version:** 2.0
**Date:** 2026-01-18
**Target Version:** life-game v0.1.0
