from dataclasses import dataclass
from typing import List

from typing_extensions import override

from .node import Node


@dataclass(frozen=True)
class Connection:
    nodes: List[Node]
    capacity: int

    @override
    def __str__(self) -> str:
        return f"{self.nodes[0].name}-{self.nodes[1].name}"

    @override
    def __hash__(self) -> int:
        return hash(self.nodes[0].name) + hash(self.nodes[1].name)
