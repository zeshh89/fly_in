from __future__ import annotations
from typing import List, Dict, Optional


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
        self.neighbors: List[Connection] = []

    def __repr__(self) -> str:
        return f"Zone({self.name})"

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Zone):
            return NotImplemented
        return self.name == other.name


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

    def get_other_zone(self, current: Zone) -> Zone:
        if current == self.zone1:
            return self.zone2
        return self.zone1

    def __repr__(self) -> str:
        return f"Connection({self.zone1.name} <-> {self.zone2.name})"


class Graph:

    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.start: Optional[Zone] = None
        self.end: Optional[Zone] = None
        self.nb_drones: Optional[int] = None

    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            raise ValueError(f"Duplicate zone: {zone.name}")
        self.zones[zone.name] = zone

    def get_zone(self, name: str) -> Zone:
        if name not in self.zones:
            raise ValueError(f"Undefined zone: {name}")
        return self.zones[name]

    def add_connection(self, connection: Connection) -> None:
        new_conn = {connection.zone1, connection.zone2}
        for conn in self.connections:
            if {conn.zone1, conn.zone2} == new_conn:
                raise ValueError("Duplicate connection")

        self.connections.append(connection)

        connection.zone1.neighbors.append(connection)
        connection.zone2.neighbors.append(connection)

    def get_neighbors(self, zone: Zone) -> List[Zone]:
        """Returning all adjacent zones"""
        return [
            conn.get_other_zone(zone) for conn in zone.neighbors
        ]

    def get_connection(self, z1: Zone, z2: Zone) -> Connection:
        for conn in z1.neighbors:
            if conn.get_other_zone(z1) == z2:
                return conn
        raise ValueError("No connection between zones")
