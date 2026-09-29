from dataclasses import dataclass
from typing import List

from .connection import Connection
from .drone import Drone
from .node import Node


@dataclass(frozen=True)
class Map:
    """Parsed map.

    Attributes:
        nb_drones: Number of drones.
        entry_point: Start hub.
        exit_point: End hub.
        nodes: All zones, hubs included.
        connections: All connections.
        drones: All drones.
    """

    nb_drones: int
    entry_point: Node
    exit_point: Node
    nodes: List[Node]
    connections: List[Connection]
    drones: List[Drone]
