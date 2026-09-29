from dataclasses import dataclass
from typing import List

from typing_extensions import override

from .node import Node


@dataclass(frozen=True)
class Connection:
    """Bidirectional link between two zones.

    Attributes:
        nodes: The two connected zones.
        capacity: Maximum number of drones using the link in the same turn.
    """

    nodes: List[Node]
    capacity: int

    @override
    def __str__(self) -> str:
        """Return the connection name, as `<zone1>-<zone2>`."""
        return f"{self.nodes[0].name}-{self.nodes[1].name}"

    @override
    def __hash__(self) -> int:
        """Return a hash that does not depend on the zone order."""
        return hash(self.nodes[0].name) + hash(self.nodes[1].name)
