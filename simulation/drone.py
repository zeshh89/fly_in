from typing import List
from models.core import Zone


class DroneState:
    def __init__(self, drone_id: int, path: List[Zone]) -> None:
        self.id = drone_id
        self.path = path
        self.position = 0
        self.finished = False
        self.in_transit = False
        self.remaining_turns = 0
        self.target_zone: Zone | None = None

    def current_zone(self) -> Zone:
        return self.path[self.position]

    def next_zone(self) -> Zone | None:
        if self.position + 1 < len(self.path):
            return self.path[self.position + 1]
        return None
