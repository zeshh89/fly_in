from parser import parse_input
from pathfind.djikstra import generate_k_paths
from assigment.scheduler import Scheduler
from simulation.engine import SimulationEngine


def main() -> None:
    filepath = "maps/map2.txt"  # cambia aquí para probar mapas

    # 1. Parse
    graph = parse_input(filepath)

    print("=== GRAPH INFO ===")
    print("Start:", graph.start)
    print("End:", graph.end)
    print("Drones:", graph.nb_drones)

    # 2. Generate paths
    paths = generate_k_paths(graph, k=3)

    print("\n=== PATHS FOUND ===")
    for i, path in enumerate(paths):
        print(f"Path {i}: ", end="")
        for zone in path:
            print(zone.name, end=" -> ")
        print("END")

    # 3. Assign drones
    scheduler = Scheduler(paths)
    assignments = scheduler.assign(graph.nb_drones)

    print("\n=== ASSIGNMENTS ===")
    for drone_id, path in assignments.items():
        print(f"D{drone_id}: {[z.name for z in path]}")

    # 4. Run simulation
    print("\n=== SIMULATION ===")
    engine = SimulationEngine(graph, assignments)
    engine.run()

    print(f"\nFinished in {engine.turn} turns")


if __name__ == "__main__":
    main()
