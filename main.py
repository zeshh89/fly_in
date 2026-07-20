import sys

from parser import parse_input, ParsingError
from pathfind.djikstra import generate_k_paths, compute_k
from assigment.scheduler import Scheduler
from simulation.engine import SimulationEngine
from visualization.renderer import Renderer


def main() -> None:

    if len(sys.argv) > 1:
        map_path = sys.argv[1]
    else:
        map_path = "maps/default.txt"

    try:
        graph = parse_input(map_path)
        print(f"Loaded map: {map_path}")

        nb_drones = graph.nb_drones or 5

        k = compute_k(graph, nb_drones)
        paths = generate_k_paths(graph, k)

        print(f"Generated {len(paths)} paths (k={k})")

        scheduler = Scheduler(paths)
        assignments = scheduler.assign(nb_drones)

        sim = SimulationEngine(graph, assignments)
        history = sim.run()

        renderer = Renderer(graph)
        renderer.run(history, sim.drones)

    except ParsingError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
