import sys

from parser import parse_input
from pathfind.djikstra import generate_k_paths, compute_k
from assigment.scheduler import Scheduler
from simulation.engine import SimulationEngine
from visualization.renderer import Renderer


def main():

    if len(sys.argv) > 1:
        map_path = sys.argv[1]
    else:
        map_path = "maps/easy/01_linear_path.txt"

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


if __name__ == "__main__":
    main()
