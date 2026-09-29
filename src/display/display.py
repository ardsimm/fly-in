from abc import ABC
from typing import Tuple

from src.graph import Graph


class Display(ABC):
    """Abstract base class for a display (not used yet)."""

    dimensions: Tuple[int, int]
    graph: Graph

    def __init__(self, dimensions: Tuple[int, int], graph: Graph) -> None:
        """Initialise the display.

        Args:
            dimensions: Width and height of the display.
            graph: Graph to display.
        """
        self.dimensions = dimensions
        self.graph = graph
