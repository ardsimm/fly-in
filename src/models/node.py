from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Node:
    name: str
    color: str
    x: int
    y: int
    max_drones: int
    priority: int
    connections: List["Connection"]
