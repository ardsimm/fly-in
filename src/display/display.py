from abc import ABC
from typing import Tuple
from src.graph import Graph


class Display(ABC):

    dimensions: Tuple[int, int]
    graph: Graph

    def __init__(self, dimensions: Tuple[int, int], graph: Graph) -> None:
        self.dimensions = dimensions
        self.graph = graph
