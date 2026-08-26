from dataclasses import dataclass
from typing import List
from .node import Node
from .connection import Connection


@dataclass(frozen=True)
class Map:
    entry_point: Node
    exit_point: Node
    nodes: List[Node]
    connections: List[Connection]
