from typing import Dict, List
from models.core import Connection, Zone, Graph
from simulation.drone import DroneState


class SimulationEngine:
    def __init__(
            self,
            graph: Graph,
            assignments: Dict[int, List[Zone]]
    ) -> None:
        self.graph = graph
        self.drones: List[DroneState] = [
            DroneState(drone_id, path)
            for drone_id, path in assignments.items()
        ]

        self.turn = 0

    def _all_finished(self) -> bool:
        return all(drone.finished for drone in self.drones)

    def _compute_turn(self) -> List[tuple[DroneState, Zone]]:
        moves: List[tuple[DroneState, Zone]] = []
        future_occupancy: Dict[Zone, int] = {}
        connection_usage: Dict[Connection, int] = {}
        planned_moves: Dict[Zone, DroneState] = {}
        processed: set[DroneState] = set()

        for drone in self.drones:
            if drone in processed:
                continue
            if drone.in_transit:
                drone.remaining_turns -= 1
                if drone.remaining_turns <= 0:
                    drone.in_transit = False
                    target = drone.target_zone
                    drone.target_zone = None

                    if target is None:
                        processed.add(drone)
                        continue
                    conn = self.graph.get_connection(
                        drone.current_zone(),
                        target
                    )
                    if not self._can_move(
                        drone,
                        target,
                        future_occupancy,
                        connection_usage
                    ):
                        processed.add(drone)
                        continue
                    moves.append((drone, target))
                    future_occupancy[target] = (
                        future_occupancy.get(target, 0) + 1
                    )
                    if conn:
                        connection_usage[conn] = (
                            connection_usage.get(conn, 0) + 1
                        )
                processed.add(drone)            
                continue

            if drone.finished:
                processed.add(drone)
                continue

            next_zone = drone.next_zone()

            if next_zone is None:
                drone.finished = True
                processed.add(drone)
                continue

            conn = self.graph.get_connection(
                drone.current_zone(),
                next_zone
            )

            if next_zone.zone_type == "restricted":
                if not self._can_move(
                    drone,
                    next_zone,
                    future_occupancy,
                    connection_usage
                ):
                    processed.add(drone)               
                    continue

                if next_zone in planned_moves:
                    processed.add(drone)
                    continue
                planned_moves[next_zone] = drone

                drone.in_transit = True
                drone.remaining_turns = 2
                drone.target_zone = next_zone
                future_occupancy[next_zone] = (
                    future_occupancy.get(next_zone, 0) + 1
                )
                if conn:
                    connection_usage[conn] = connection_usage.get(conn, 0) + 1

                processed.add(drone)
                continue

            if self._can_move(
                drone,
                next_zone,
                future_occupancy,
                connection_usage
            ):
                if next_zone in planned_moves:
                    processed.add(drone)
                    continue
                planned_moves[next_zone] = drone

                moves.append((drone, next_zone))
                future_occupancy[next_zone] = (
                    future_occupancy.get(next_zone, 0) + 1
                )
                if conn:
                    connection_usage[conn] = connection_usage.get(conn, 0) + 1
            processed.add(drone)

        return moves

    def _can_move(
            self,
            drone: DroneState,
            next_zone: Zone,
            future_occupancy: Dict[Zone, int],
            connection_usage: Dict[Connection, int]
    ) -> bool:

        for other in self.drones:
            if other is drone:
                continue

            if (
                other.current_zone() == next_zone
                and other.next_zone() == drone.current_zone()
            ):

                if drone.id > other.id:
                    return False

        if next_zone == self.graph.end:
            return True

        current = future_occupancy.get(next_zone, 0)

        if current >= next_zone.capacity:
            return False

        conn = self.graph.get_connection(
            drone.current_zone(),
            next_zone
        )
        used = connection_usage.get(conn, 0)
        if used >= conn.capacity:
            return False

        return True

    def _aply_moves(self, moves: List[tuple[DroneState, Zone]]) -> None:
        for drone, next_zone in moves:
            drone.position += 1

            drone.in_transit = False
            drone.target_zone = None
            drone.remaining_turns = 0

            if next_zone == self.graph.end:
                drone.finished = True

    def _print_turn(
            self,
            moves: List[tuple[DroneState, Zone]]
    ) -> None:

        output = []
        for drone, zone in moves:
            output.append(f"D{drone.id} -> {zone.name}")

        if output:
            print(" ".join(output))

    def run(self) -> None:
        """Run simulation untill all drones reach teh end"""
        history_positions = []

        while not self._all_finished():
            self.turn += 1
            moves = self._compute_turn()
            self._aply_moves(moves)
            self._print_turn(moves)

            history_positions.append({
                drone.id: drone.current_zone()
                for drone in self.drones
            })
        return history_positions
