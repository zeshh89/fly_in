from typing import List, Dict, Optional


class ParsingError(Exception):
    """Custom exception for parsing errors"""
    pass


class Zone:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        capacity: int = 1,
        color: Optional[str] = None,
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.capacity = capacity
        self.color = color


class Connection:
    def __init__(
            self,
            zone1: Zone,
            zone2: Zone,
            capacity: int = 1
    ) -> None:
        self.zone1 = zone1
        self.zone2 = zone2
        self.capacity = capacity


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.start: Optional[Zone] = None
        self.end: Optional[Zone] = None
        self.nb_drones: Optional[int] = None

    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            raise ParsingError(f"Duplicate zone: {zone.name}")
        self.zones[zone.name] = zone

    def get_zone(self, name: str) -> Zone:
        if name not in self.zones:
            raise ParsingError(f"Undefined zone: {name}")
        return self.zones[name]

    def add_connection(self, connection: Connection) -> None:
        new_conn = {connection.zone1, connection.zone2}
        for conn in self.connections:
            if {conn.zone1, conn.zone2} == new_conn:
                raise ParsingError("Duplicate connection")

        self.connections.append(connection)


def preprocess_line(line: str) -> str:
    """Remove comments and strip whitespace"""
    line = line.split("#")[0]
    return line.strip()


def parse_metadata(metadata_str: str) -> Dict:
    """Parse metadata inside brackets"""
    metadata_str = metadata_str.strip("[]")
    metadata = {}

    if not metadata_str:
        return metadata

    parts = metadata_str.split()
    for part in parts:
        if "=" not in part:
            raise ParsingError(f"Invalid metadata: {part}")
        key, value = part.split("=", 1)
        metadata[key] = value

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


def parse_zone(line: str, graph: Graph, zone_kind: str) -> None:
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

        zone_type = metadata.get("type", "normal")
        if zone_type not in {"normal", "blocked", "restricted", "priority"}:
            raise ParsingError(f"Invalid zone type: {zone_type}")

        capacity = int(metadata.get("max_drones", 1))
        if capacity <= 0:
            raise ParsingError("Invalid capacity value")

        color = metadata.get("color")
        zone = Zone(name, x, y, zone_type, capacity, color)
        graph.add_zone(zone)

        if zone_kind == "start":
            if graph.start is not None:
                raise ParsingError("Multiple start zones defined")
            graph.start = zone

        elif zone_kind == "end":
            if graph.end is not None:
                raise ParsingError("Multiple end zones defined")
            graph.end = zone

    except ValueError:
        raise ParsingError("Invalid numeric value in zone")


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


def parse_input(filepath: str) -> Graph:
    graph = Graph()

    with open(filepath, "r") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = preprocess_line(raw_line)

            if not line:
                continue

            line = line.lower()

            if line.startswith("nb_drones:"):
                parse_nb_drones(line, graph)

            elif line.startswith("start_hub"):
                parse_zone(line, graph, "start")

            elif line.startswith("end_hub"):
                parse_zone(line, graph, "end")

            elif line.startswith("hub"):
                parse_zone(line, graph, "normal")

            elif line.startswith("connection"):
                parse_connection(line, graph)

            else:
                raise ParsingError(f"Unknown line type : {line_number}")

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

    return graph


def main() -> None:
    filepath = "map1.txt"  # tu archivo de prueba

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

    except ParsingError as e:
        print(f"Error parsing file: {e}")


if __name__ == "__main__":
    main()
