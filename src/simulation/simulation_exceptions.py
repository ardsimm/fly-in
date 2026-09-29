class SimulationException(Exception):
    """Base class of the simulation errors."""


class PathNotFoundError(SimulationException):
    """Raised when no path leads to the end hub."""


class InvalidMoveError(SimulationException):
    """Raised when a schedule breaks a movement rule."""
