from abc import ABC, abstractmethod
from src.graph import Graph


class Solver(ABC):
    graph: Graph

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    @abstractmethod
    def solve(self) -> None:
        pass
