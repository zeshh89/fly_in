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

    def _zone_occupancy(self, zone: Zone) -> int:
        count = 0

        for drone in self.drones:

            if drone.finished:
                continue

            # drones ya estacionados
            if not drone.in_transit:
                if drone.current_zone() == zone:
                    count += 1

        return count

    def _connection_usage(
        self,
        connection: Connection
    ) -> int:

        count = 0

        for drone in self.drones:

            if not drone.in_transit:
                continue

            if (
                drone.source_zone == connection.zone1
                and drone.target_zone == connection.zone2
            ) or (
                drone.source_zone == connection.zone2
                and drone.target_zone == connection.zone1
            ):
                count += 1

        return count

    def _can_move(
        self,
        drone: DroneState,
        next_zone: Zone
    ) -> bool:

        # END sin límite
        if next_zone == self.graph.end:
            return True

        # capacidad HUB
        occupancy = self._zone_occupancy(next_zone)

        if occupancy >= next_zone.capacity:
            return False

        # capacidad LINK
        conn = self.graph.get_connection(
            drone.current_zone(),
            next_zone
        )

        usage = self._connection_usage(conn)

        if usage >= conn.capacity:
            return False

        return True

    def _update_transit(self) -> List[tuple[DroneState, Zone]]:

        arrived_moves = []

        for drone in self.drones:

            if not drone.in_transit:
                continue

            drone.remaining_turns -= 1

            if drone.remaining_turns > 0:
                continue

            # llegada final
            drone.in_transit = False

            if drone.target_zone is None:
                continue

            arrived_zone = drone.target_zone

            drone.position += 1

            if arrived_zone.zone_type == "restricted":
                drone.wait_turns = 1

            arrived_moves.append((drone, arrived_zone))

            if arrived_zone == self.graph.end:
                drone.finished = True

        return arrived_moves

    def _start_new_moves(
        self,
        arrived_this_turn: set[DroneState]
    ) -> List[tuple[DroneState, Zone]]:

        started_moves = []

        for drone in self.drones:
            if drone in arrived_this_turn:
                continue

            if drone.finished:
                continue

            if drone.in_transit:
                continue

            if drone.wait_turns > 0:
                drone.wait_turns -= 1
                continue

            next_zone = drone.next_zone()

            if next_zone is None:
                drone.finished = True
                continue

            if not self._can_move(drone, next_zone):
                continue

            travel_time = 1

            drone.in_transit = True
            drone.remaining_turns = travel_time

            drone.source_zone = drone.current_zone()
            drone.target_zone = next_zone

            started_moves.append((drone, next_zone))

        return started_moves

    def _print_turn(
        self,
        started_moves: List[tuple[DroneState, Zone]],
        arrived_moves: List[tuple[DroneState, Zone]]
    ) -> None:

        output = []

        for drone, zone in started_moves:

            if zone.zone_type == "restricted":
                output.append(
                    f"D{drone.id} entering {zone.name}"
                )
            else:
                output.append(
                    f"D{drone.id} -> {zone.name}"
                )

        for drone, zone in arrived_moves:

            if zone.zone_type == "restricted":
                output.append(
                    f"D{drone.id} arrived {zone.name}"
                )

        if output:
            print(" | ".join(output))

    def run(self):

        history = []

        # estado inicial
        history.append({
            drone.id: drone.current_zone()
            for drone in self.drones
        })

        while not self._all_finished():

            arrived_moves = self._update_transit()

            arrived_drones = {
                drone for drone, _ in arrived_moves
            }

            started_moves = self._start_new_moves(
                arrived_drones
            )

            self._print_turn(
                started_moves,
                arrived_moves
            )

            # SOLO guardar cuando cambia posición real
            if arrived_moves:

                history.append({
                    drone.id: drone.current_zone()
                    for drone in self.drones
                })

                self.turn += 1

            for drone, _ in arrived_moves:
                drone.source_zone = None
                drone.target_zone = None

        return history
