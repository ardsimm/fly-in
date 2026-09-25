class SimulationException(Exception):
    pass


class PathNotFoundError(SimulationException):
    pass


class InvalidMoveError(SimulationException):
    pass
