from src.models import Map, Node


class Graph:
    """Entry and exit points of a map (not used yet)."""

    root: Node
    exit: Node

    def __init__(self, map: Map) -> None:
        """Initialise the graph from a map.

        Args:
            map: Parsed map.
        """
        self.root = map.entry_point
        self.exit = map.exit_point
