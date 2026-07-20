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
            result += f"\n>> {self.line}"
        return result


def preprocess_line(line: str) -> str:
    """Remove comments and strip whitespace"""
    line = line.split("#")[0]
    return line.strip()


def parse_metadata(metadata_str: str) -> Dict[str, str]:
    """Parse metadata inside brackets"""
    metadata_str = metadata_str.strip("[]").strip()
    metadata: Dict[str, str] = {}

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
        raise ParsingError("Invalid number of drones") from None


def parse_zone(line: str, graph: Graph, role: str | None = None) -> None:

    if "[" in line:
        main_part, metadata_part = line.split("[", 1)
        metadata = parse_metadata("[" + metadata_part)
    else:
        main_part = line
        metadata = {}
    allowed_metadata = {
        "zone",
        "max_drones",
        "color",
    }

    for key in metadata:
        if key not in allowed_metadata:
            raise ParsingError(
                f"Unknown zone metadata: {key}"
            )

    tokens = main_part.split()

    if len(tokens) < 4:
        raise ParsingError("Invalid zone format")

    name = tokens[1]

    if "-" in name:
        raise ParsingError("Zone name cannot contain '-'")

    try:
        x = int(tokens[2])
        y = int(tokens[3])
    except ValueError:
        raise ParsingError(
            "Invalid numeric value in zone definition"
        ) from None

    zone_type = metadata.get("zone", "normal").strip().lower()

    if zone_type not in {
        "normal",
        "blocked",
        "restricted",
        "priority"
    }:
        raise ParsingError(f"Invalid zone type: {zone_type}")

    try:
        capacity = int(metadata.get("max_drones", 1))
    except ValueError:
        raise ParsingError(
            "Invalid zone capacity"
        ) from None

    if capacity <= 0:
        raise ParsingError("Invalid zone capacity")

    VCOLORS = {
            "red": (220, 50, 50),
            "darkred": (139, 0, 0),
            "blue": (50, 120, 220),
            "green": (50, 200, 50),
            "purple": (160, 80, 200),
            "orange": (255, 140, 0),
            "yellow": (240, 220, 60),
            "gold": (255, 200, 0),
            "violet": (180, 80, 255),
            "black": (30, 30, 30),
            "white": (240, 240, 240),
            "brown": (139, 90, 43),
            "maroon": (128, 0, 0),
            "rainbow": (200, 200, 200),
            "cyan": (50, 200, 200),
            "lime": (50, 255, 50),
            "magenta": (255, 0, 255)
        }

    color = metadata.get("color")

    if color is not None:
        color = color.strip().lower()

        if color not in VCOLORS:
            raise ParsingError(
                f"Invalid color: {color}"
            )

    zone = Zone(name, x, y, zone_type, capacity, color)

    try:
        graph.add_zone(zone)
    except ValueError as e:
        raise ParsingError(str(e)) from None
    if role == "start":
        if graph.start is not None:
            raise ParsingError("Multiple start_hub defined")
        graph.start = zone

    elif role == "end":
        if graph.end is not None:
            raise ParsingError("Multiple end_hub defined")
        graph.end = zone


def parse_connection(line: str, graph: Graph) -> None:

    if "[" in line:
        main_part, metadata_part = line.split("[", 1)
        metadata = parse_metadata("[" + metadata_part)
    else:
        main_part = line
        metadata = {}

    allowed = {"max_link_capacity"}

    for key in metadata:
        if key not in allowed:
            raise ParsingError(
                f"Unknown connection metadata: {key}"
            )

    tokens = main_part.split()

    if len(tokens) != 2:
        raise ParsingError("Invalid connection format")

    names = tokens[1].split("-")

    if len(names) != 2:
        raise ParsingError("Invalid connection")

    zone1 = graph.get_zone(names[0])
    zone2 = graph.get_zone(names[1])

    if zone1 is None:
        raise ParsingError(f"Unknown zone: {names[0]}")

    if zone2 is None:
        raise ParsingError(f"Unknown zone: {names[1]}")

    try:
        capacity = int(metadata.get("max_link_capacity", 1))
    except ValueError:
        raise ParsingError(
            "Invalid connection capacity"
        ) from None

    if capacity <= 0:
        raise ParsingError("Invalid connection capacity")

    connection = Connection(zone1, zone2, capacity)

    try:
        graph.add_connection(connection)
    except ValueError as e:
        raise ParsingError(str(e)) from None


def has_connection(zone: Zone, connections: List[Connection]) -> bool:
    """Check if a zone has at least one connection"""
    for conn in connections:
        if conn.zone1 == zone or conn.zone2 == zone:
            return True
    return False


def bfs_path(graph: Graph) -> bool:
    """Check if there is a path from start to end using BFS"""

    if graph.start is None or graph.end is None:
        raise ValueError(
            "Graph must have start and end zones defined"
        ) from None

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
