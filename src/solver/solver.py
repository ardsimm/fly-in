from abc import ABC, abstractmethod

from src.graph import Graph


class Solver(ABC):
    """Abstract base class for a solver (not used yet)."""

    graph: Graph

    def __init__(self, graph: Graph) -> None:
        """Initialise the solver.

        Args:
            graph: Graph to solve.
        """
        self.graph = graph

    @abstractmethod
    def solve(self) -> None:
        """Solve the graph."""
