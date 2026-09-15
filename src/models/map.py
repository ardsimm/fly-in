from dataclasses import dataclass
from typing import List

from .connection import Connection
from .node import Node


@dataclass(frozen=True)
class Map:
    nb_drones: int
    entry_point: Node
    exit_point: Node
    nodes: List[Node]
    connections: List[Connection]
