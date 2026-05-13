from parser import parse_input
from pathfind.djikstra import generate_k_paths
from assigment.scheduler import Scheduler
from simulation.engine import SimulationEngine
from visualization.renderer import Renderer


def main():
    graph = parse_input("maps/medium/02_circular_loop.txt")

    paths = generate_k_paths(graph, k=3)

    scheduler = Scheduler(paths)
    assignments = scheduler.assign(graph.nb_drones)

    engine = SimulationEngine(graph, assignments)
    history = engine.run()

    renderer = Renderer(graph)
    renderer.run(history, engine.drones)


if __name__ == "__main__":
    main()
