from src.models import Map, Node


class Graph:

    root: Node
    exit: Node

    def __init__(self, map: Map) -> None:
        self.root = map.entry_point
        self.exit = map.exit_point
