from parser import parse_input
from pathfind.djikstra import generate_k_paths, compute_k
from assigment.scheduler import Scheduler


def main() -> None:
    filepath = "maps/map2.txt"

    graph = parse_input(filepath)

    print("Graph:", graph)
    print("Start:", graph.start)
    print("End:", graph.end)

    k = compute_k(graph, graph.nb_drones)
    paths = generate_k_paths(graph, k)

    scheduler = Scheduler(paths)
    assignments = scheduler.assign(graph.nb_drones)

    print("\n=== MULTI PATHS ===")
    for i, path in enumerate(paths):
        print(f"Path {i + 1}:", end="")
        for zone in path:
            print(zone.name, end=" -> ")
        print("END")
    print("\n=== SUMMARY ===")
    print(f"Total paths generated: {len(paths)}")

    print("\n=== ASSIGNMENTS ===")
    for drone, path in assignments.items():
        print(f"D{drone}: " + " -> ".join(z.name for z in path))
    print("\n=== END ===")


if __name__ == "__main__":
    main()
