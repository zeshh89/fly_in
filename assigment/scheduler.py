from typing import List, Dict
from models.core import Zone


class Scheduler:
    """Scheduler for drone paths"""

    def __init__(self, paths: List[List[Zone]]) -> None:
        self.paths = paths
        self.path_loads: Dict[int, int] = {
            i: 0 for i in range(len(paths))
        }

    def assign(self, nb_drones: int) -> Dict[int, List[Zone]]:
        """Assign each drone tothe best avaible path"""
        if not self.paths:
            return {}

        assignments: Dict[int, List[Zone]] = {}

        for drone_id in range(1, nb_drones + 1):
            best_idx = self._select_best_path()
            assignments[drone_id] = self.paths[best_idx]
            self.path_loads[best_idx] += 1

        return assignments

    def _select_best_path(self) -> int:
        """Select the best path based on current loads"""
        best_idx = 0
        best_score = float("inf")

        for i, path in enumerate(self.paths):
            base_cost = len(path)
            load_penalty = self.path_loads[i]
            score = base_cost + load_penalty * 0.7

            if score < best_score:
                best_score = score
                best_idx = i

        return best_idx
