import heapq
from typing import Dict, List, Optional
from parser import Graph, Zone


def get_zone_cost(zone: Zone) -> int:
    """Calculates the cost of entering a zone"""
    if zone.zone_type == "blocked":
        return float('inf')
    if zone.zone_type == "restricted":
        return 2
    if zone.zone_type == "priority":
        return 1
    return 1


def dijkstra(graph: Graph) -> List[Zone]:
    """Find shortest path from start to end"""

    start = graph.start
    end = graph.end

    if start is None or end is None:
        raise ValueError("Graph must have start and end zones")

    distances: Dict[Zone, float] = {
        zone: float('inf') for zone in graph.zones.values()
    }

    previous: Dict[Zone, Optional[Zone]] = {
        zone: None for zone in graph.zones.values()
    }

    distances[start] = 0

    priority_queue: List[tuple[float, int, Zone]] = [(0, id(start), start)]

    while priority_queue:
        current_cost, _, current_zone = heapq.heappop(priority_queue)

        if current_zone == end:
            break
        if current_cost > distances[current_zone]:
            continue
        for conn in current_zone.neighbors:
            neighbor = conn.get_other_zone(current_zone)
            if neighbor.zone_type == "blocked":
                continue
            move_cost = get_zone_cost(neighbor)
            new_cost = current_cost + move_cost
            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous[neighbor] = current_zone
                heapq.heappush(
                    priority_queue,
                    (new_cost, id(neighbor), neighbor)
                )
    return reconstruct_path(previous, end)


def dijkstra_with_penalty(
        graph: Graph,
        penalties: Optional[Dict[Zone, float]] = None
) -> List[Zone]:
    """use node penalties for multipath"""

    start = graph.start
    end = graph.end

    if start is None or end is None:
        raise ValueError("Graph must have start and end zones")

    distances: Dict[Zone, float] = {
        zone: float('inf') for zone in graph.zones.values()
    }

    previous: Dict[Zone, Optional[Zone]] = {
        zone: None for zone in graph.zones.values()
    }

    distances[start] = 0
    priority_queue: List[tuple[float, int, Zone]] = [(0, id(start), start)]

    while priority_queue:
        current_cost, _, current_zone = heapq.heappop(priority_queue)

        if current_zone == end:
            break
        if current_cost > distances[current_zone]:
            continue
        for conn in current_zone.neighbors:
            neighbor = conn.get_other_zone(current_zone)
            if neighbor.zone_type == "blocked":
                continue
            move_cost = get_zone_cost(neighbor)

            if penalties and neighbor in penalties:
                move_cost += penalties[neighbor]
            new_cost = current_cost + move_cost

            if new_cost < distances[neighbor]:
                distances[neighbor] = new_cost
                previous[neighbor] = current_zone
                heapq.heappush(
                    priority_queue,
                    (new_cost, id(neighbor), neighbor)
                )
    return reconstruct_path(previous, end)


def reconstruct_path(
        previous: Dict[Zone, Optional[Zone]],
        end: Zone
) -> List[Zone]:
    """Reconstructs the path from start to end"""

    path: List[Zone] = []
    current: Optional[Zone] = end
    while current is not None:
        path.append(current)
        current = previous.get(current)
    path.reverse()
    return path


def build_penalties(graph: Graph) -> Dict[Zone, float]:

    penalties = {}

    for zone in graph.zones.values():
        if zone.zone_type == "priority":
            penalties[zone] = -0.5
        else:
            penalties[zone] = 0
    return penalties


def compute_k(graph: Graph, nb_drones: int) -> int:
    """Compute the number of paths to generate on an adaptative way"""
    num_nodes = len(graph.zones)
    num_edges = len(graph.connections)

    avg_degree = (2 * num_edges) / num_nodes

    base_k = int(nb_drones ** 0.5)
    k = int(min(max(2, base_k), max(2, avg_degree)))

    return k


def generate_k_paths(graph: Graph, k: int = 3) -> List[List[Zone]]:
    """Generates multiple alternative paths"""
    paths: List[List[Zone]] = []
    penalties: Dict[Zone, float] = build_penalties(graph)

    for _ in range(k):
        path = dijkstra_with_penalty(graph, penalties)

        if len(path) <= 1:
            break
        paths.append(path)

        for zone in path:
            if zone.zone_type == "priority":
                penalties[zone] -= 0.2
            else:
                penalties[zone] = penalties.get(zone, 0) + 5

    return paths
