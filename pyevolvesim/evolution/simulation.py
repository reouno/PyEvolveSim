"""Main simulation loop for the evolution simulation."""

import time
from .world import EvolutionWorld
from .renderer import EvolutionRenderer
from .stats import WorldStats
from .stats_history import StatsHistory
from .graph_renderer import GraphRenderer, GraphDisplay
from .config import ENABLE_GRAPH, GRAPH_RECORD_INTERVAL, GRAPH_HEIGHT, GRAPH_MAX_POINTS


class EvolutionSimulation:
    """Manages the evolution simulation loop.

    Coordinates between world state, rendering, and statistics tracking.
    Graph functionality is optional and loosely coupled.
    """

    def __init__(
        self,
        world: EvolutionWorld,
        delay: float = 0.2,
        enable_graph: bool = ENABLE_GRAPH,
        record_interval: int = GRAPH_RECORD_INTERVAL,
    ):
        """
        Initialize the simulation.

        Args:
            world: Initial world state
            delay: Delay between updates in seconds
            enable_graph: Whether to display graphs
            record_interval: Record stats every N generations
        """
        self.world = world
        self.delay = delay
        self.renderer = EvolutionRenderer()

        # Graph components (optional, loosely coupled)
        self.enable_graph = enable_graph
        self.record_interval = record_interval

        self.stats_history: StatsHistory | None
        self.graph_display: GraphDisplay | None

        if self.enable_graph:
            self.stats_history = StatsHistory(max_points=GRAPH_MAX_POINTS)
            graph_renderer = GraphRenderer(height=GRAPH_HEIGHT, width=GRAPH_MAX_POINTS)
            separator_width = self.world.width + 2
            self.graph_display = GraphDisplay(
                graph_renderer, separator_width=separator_width
            )
        else:
            self.stats_history = None
            self.graph_display = None

    def _should_record_stats(self) -> bool:
        """Determine if stats should be recorded at current generation."""
        return self.enable_graph and self.world.generation % self.record_interval == 0

    def _record_stats(self) -> None:
        """Record current stats to history."""
        if not self.enable_graph or self.stats_history is None:
            return

        stats = WorldStats.from_world(self.world)
        self.stats_history.record(stats)

    def _render_graphs(self) -> str:
        """Render graphs and return as string (no printing)."""
        if (
            not self.enable_graph
            or self.graph_display is None
            or self.stats_history is None
        ):
            return ""

        if self.stats_history.is_empty():
            return ""

        # Get data from history
        generations = self.stats_history.get_generations()
        creature_counts = self.stats_history.get_values("creature_count")
        avg_speeds = self.stats_history.get_values("avg_speed")
        std_speeds = self.stats_history.get_values("std_speed")

        # Render and RETURN (don't print)
        return self.graph_display.render_evolution_graphs(
            generations, creature_counts, avg_speeds, std_speeds
        )

    def run(self) -> None:
        """Run the simulation loop until Ctrl+C or extinction."""
        # Enter alternate screen buffer (professional TUI)
        print("\033[?1049h", end="", flush=True)

        try:
            while True:
                # Record stats if needed
                if self._should_record_stats():
                    self._record_stats()

                # --- ATOMIC FRAME ASSEMBLY ---
                # Calculate stats once per frame (reused for render and history)
                stats = WorldStats.from_world(self.world)

                # Build complete frame in memory (no printing yet!)
                terminal_codes = self.renderer.clear_screen()
                world_frame = self.renderer.render(self.world, stats)
                graph_frame = self._render_graphs() if self.enable_graph else ""

                # Assemble complete frame
                complete_frame = terminal_codes + world_frame
                if graph_frame:
                    complete_frame += "\n" + graph_frame

                # SINGLE ATOMIC WRITE - This is the critical fix!
                print(complete_frame, end="", flush=True)
                # --- END ATOMIC FRAME ASSEMBLY ---

                # Check for extinction
                if len(self.world.creatures) == 0:
                    # Exit alt screen and show cursor
                    cleanup = "\033[?1049l" + self.renderer.show_cursor()
                    print(cleanup, end="", flush=True)
                    print("\nExtinction! All creatures have died.")
                    break

                # Wait and update
                time.sleep(self.delay)
                self.world = self.world.next_step()

        except KeyboardInterrupt:
            # Exit alt screen and show cursor
            cleanup = "\033[?1049l" + self.renderer.show_cursor()
            print(cleanup, end="", flush=True)
            print("\n\nSimulation stopped by user.")
            print(f"Final generation: {self.world.generation}")
            print(f"Final creature count: {len(self.world.creatures)}")

        finally:
            # Ensure we always exit alternate screen
            print("\033[?1049l", end="", flush=True)
