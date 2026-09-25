from dataclasses import dataclass
from typing import List

from .node import Node


@dataclass(frozen=True)
class Connection:
    nodes: List[Node]
    capacity: int

    def __hash__(self) -> int:
        return hash(self.nodes[0].name) + hash(self.nodes[1].name)
