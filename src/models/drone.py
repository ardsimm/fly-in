from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import override


@dataclass
class Drone:
    """Drone to route from the start hub to the end hub.

    Attributes:
        id: Unique identifier, starting at 1.
        name: Display name.
        done: Whether a path to the end hub has been found.
    """

    id: int
    name: str
    done: bool = False

    @override
    def __hash__(self) -> int:
        """Return a hash based on the drone id."""
        return hash(self.id)

    @override
    def __str__(self) -> str:
        """Return the drone name used in the output, as `D<id>`."""
        return f"D{self.id}"
