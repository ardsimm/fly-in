from dataclasses import dataclass
from typing import List
from .connection import Connection


@dataclass(frozen=True)
class Node:
    name: str
    color: str
    x: int
    y: int
    priority: int
    connections: List[Connection]
