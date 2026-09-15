from dataclasses import dataclass, field
from heapq import heappush
from typing import Dict, List, Optional, Set, Tuple, Union

from src.models.connection import Connection
from src.models.drone import Drone
from src.models.node import Node

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

# Predecessor map used by the plain BFS (solvability check)
PrevDict = Dict[Node, Node]

# What a drone can occupy during a turn: a zone or a connection
Step = Union[Node, Connection]
Path = List[Step]

# Per-turn occupancy: step -> number of drones
TurnAllocation = Dict[Step, int]
AllocationTable = Dict[int, TurnAllocation]

# (connection being crossed, restricted destination zone) while in transit
Transit = Tuple[Optional[Connection], Optional[Node]]
NO_TRANSIT: Transit = (None, None)

# (turn, insertion index, current node or None when in transit, transit)
QueueEntry = Tuple[int, int, Optional[Node], Transit]

# (departure turn, reached step) -> (previous step, connection used)
CooperativePrevKey = Tuple[int, Step]
CooperativePrevValue = Tuple[Step, Optional[Connection]]
CooperativePrevDict = Dict[CooperativePrevKey, CooperativePrevValue]


# ---------------------------------------------------------------------------
# Per-drone search state
# ---------------------------------------------------------------------------


@dataclass
class DroneSearch:
    """Mutable state of the path search for a single drone."""

    drone: Drone
    queue: List[QueueEntry]
    visited: Set[Node]
    prev_nodes: CooperativePrevDict = field(default_factory=dict)
    insertion_idx: int = 1

    @classmethod
    def start(cls, drone: Drone, entry_point: Node) -> "DroneSearch":
        """Create a search whose only pending state is the entry point."""
        return cls(
            drone=drone,
            queue=[(0, 0, entry_point, NO_TRANSIT)],
            visited={entry_point},
        )

    def push(
        self,
        turn: int,
        node: Optional[Node],
        transit: Transit = NO_TRANSIT,
    ) -> None:
        """Queue a state; the insertion index breaks ties between turns."""
        self.insertion_idx += 1
        heappush(self.queue, (turn, self.insertion_idx, node, transit))
