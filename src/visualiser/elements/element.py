from abc import ABC, abstractmethod


class Element(ABC):
    """Base class of the drawable elements."""

    z_index: int

    def __init__(self) -> None:
        """Initialise the element with a z_index of 0."""
        self.z_index = 0

    @abstractmethod
    def draw(self) -> None:
        """Draw the element on the screen."""

    def update(self, dt: int, combined_dt: int) -> None:
        """Update the element state; does nothing by default.

        Args:
            dt: Time since the last frame, in milliseconds.
            combined_dt: Time since the start, in milliseconds.
        """
