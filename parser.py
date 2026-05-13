from typing import List, Dict
from collections import deque
from models.core import Graph, Zone, Connection


class ParsingError(Exception):
    """Custom exception for parsing errors"""

    def __init__(
            self,
            message: str,
            line: str | None = None,
            line_number: int | None = None
    ) -> None:
        self.message = message
        self.line = line
        self.line_number = line_number
        super().__init__(self.__str__())

    def __str__(self) -> str:
        result = ""
        if self.line_number is not None:
            result += f"Line {self.line_number}: "

        result += self.message
        if self.line is not None:
            result += f"\n>> {self.line})"
        return result


def preprocess_line(line: str) -> str:
    """Remove comments and strip whitespace"""
    line = line.split("#")[0]
    return line.strip()


def parse_metadata(metadata_str: str) -> Dict:
    """Parse metadata inside brackets"""
    metadata_str = metadata_str.strip("[]").strip()
    metadata = {}

    if not metadata_str:
        return metadata

    parts = metadata_str.replace(",", " ").replace(";", " ").split()

    for part in parts:
        if "=" not in part:
            raise ParsingError(f"Invalid metadata: {part}")
        key, value = [x.strip() for x in part.split("=", 1)]
        metadata[key.strip().lower()] = value.strip()

    return metadata


def parse_nb_drones(line: str, graph: Graph) -> None:
    """Parse the number of drones"""
    try:
        _, value = line.split(":", 1)
        nb = int(value.strip())
        if nb <= 0:
            raise ValueError
        graph.nb_drones = nb
    except ValueError:
        raise ParsingError("Invalid number of drones")


def parse_zone(line: str, graph: Graph, role: str | None = None) -> None:
    """Parse a zone definition"""
    try:
        if "[" in line:
            main_part, metadata_part = line.split("[", 1)
            metadata = parse_metadata("[" + metadata_part)
        else:
            main_part = line
            metadata = {}

        tokens = main_part.split()
        if len(tokens) < 4:
            raise ParsingError("Invalid zone format")

        name = tokens[1]
        if "-" in name:
            raise ParsingError("Zone name cannot contain '-'")

        x = int(tokens[2])
        y = int(tokens[3])


        zone_type = metadata.get("zone", "normal")
        zone_type = zone_type.strip().lower()
        if zone_type not in {"normal", "blocked", "restricted", "priority"}:
            raise ParsingError(f"Invalid zone type: {zone_type}")
        capacity = int(metadata.get("max_drones", 1))
        if capacity <= 0:
            raise ParsingError("Invalid zone capacity")
        color = metadata.get("color")
        zone = Zone(name, x, y, zone_type, capacity, color)
        graph.add_zone(zone)

        if role == "start":
            if graph.start is not None:
                raise ParsingError("Multiple start_hub defined")
            graph.start = zone
        elif role == "end":
            if graph.end is not None:
                raise ParsingError("Multiple end_hub defined")
            graph.end = zone
        print("LINE:", line)
        print("METADATA:", metadata)
        print("TYPE:", zone_type)

    except ValueError:
        raise ParsingError("Invalid numeric value in zone definition")


def parse_connection(line: str, graph: Graph) -> None:

    try:
        if "[" in line:
            main_part, metadata_part = line.split("[", 1)
            metadata = parse_metadata("[" + metadata_part)
        else:
            main_part = line
            metadata = {}

        tokens = main_part.split()
        if len(tokens) != 2:
            raise ParsingError("Invalid connection format")

        names = tokens[1].split("-")
        if len(names) != 2:
            raise ParsingError("Invalid connection")

        zone1 = graph.get_zone(names[0])
        zone2 = graph.get_zone(names[1])

        capacity = int(metadata.get("max_link_capacity", 1))
        if capacity <= 0:
            raise ParsingError("Invalid connection capacity ")

        connection = Connection(zone1, zone2, capacity)
        graph.add_connection(connection)

    except ValueError:
        raise ParsingError("Invalid numeric value in connection")


def has_connection(zone: Zone, connections: List[Connection]) -> bool:
    """Check if a zone has at least one connection"""
    for conn in connections:
        if conn.zone1 == zone or conn.zone2 == zone:
            return True
    return False


def bfs_path(graph: Graph) -> bool:
    """Check if there is a path from start to end using BFS"""

    if graph.start is None or graph.end is None:
        raise ValueError("Graph must have start and end zones defined")

    queue = deque([graph.start])
    visited = set([graph.start])

    while queue:
        current = queue.popleft()
        if current == graph.end:
            return True

        for conn in current.neighbors:
            neighbor = conn.get_other_zone(current)
            if neighbor.zone_type == "blocked":
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False


def parse_input(filepath: str) -> Graph:
    graph = Graph()

    with open(filepath, "r") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = preprocess_line(raw_line)

            if not line:
                continue

            line = line.lower()

            try:

                if line.startswith("nb_drones:"):
                    parse_nb_drones(line, graph)
                elif line.startswith("start_hub"):
                    parse_zone(line, graph, "start")
                elif line.startswith("end_hub"):
                    parse_zone(line, graph, "end")

                elif line.startswith("hub"):
                    parse_zone(line, graph)

                elif line.startswith("connection"):
                    parse_connection(line, graph)

                else:
                    raise ParsingError(f"Unknown line type : {line_number}")
            except ParsingError as e:

                if e.line is None:
                    raise ParsingError(
                        e.message,
                        raw_line.strip(),
                        line_number
                    )
                raise

    if graph.start is None:
        raise ParsingError("Missing start_hub")
    if graph.end is None:
        raise ParsingError("Missing end_hub")
    if graph.nb_drones is None:
        raise ParsingError("Missing nb_drones")

    if not has_connection(graph.start, graph.connections):
        raise ParsingError("Start_hub has not connections")
    if not has_connection(graph.end, graph.connections):
        raise ParsingError("End_hub has not connections")
    if not bfs_path(graph):
        raise ParsingError("No path from start to end")
    else:
        print("Valid graph: path exists from start to end")

    return graph


def main() -> None:
    filepath = "map2.txt"

    try:
        graph = parse_input(filepath)
        print(f"Number of drones: {graph.nb_drones}")
        print(
            f"Start zone: {graph.start.name} "
            f"({graph.start.x}, {graph.start.y})"
        )
        print(f"End zone: {graph.end.name} ({graph.end.x}, {graph.end.y})")
        print("\nZones:")
        for zone_name, zone in graph.zones.items():
            print(
                f" - {zone_name}: type={zone.zone_type},"
                f" capacity={zone.capacity}, color={zone.color}"
            )

        print("\nConnections:")
        for conn in graph.connections:
            print(
                f" - {conn.zone1.name} <-> {conn.zone2.name}, "
                f"capacity={conn.capacity}"
            )
        print("\nNeighbors per zone:")
        for zone in graph.zones.values():
            neighbors = [
                conn.get_other_zone(zone).name
                for conn in zone.neighbors
            ]

            print(f"{zone.name} -> {neighbors}")

    except ParsingError as e:
        print(f"Error parsing file: {e}")


if __name__ == "__main__":
    main()
