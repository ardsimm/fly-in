from abc import ABC, abstractmethod


class Element(ABC):

    z_index: int

    def __init__(self) -> None:
        self.z_index = 0

    @abstractmethod
    def draw(self) -> None:
        pass

    def update(self, dt: int, combined_dt: int) -> None:
        pass
