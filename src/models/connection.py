from dataclasses import dataclass
from typing import List

from .node import Node


@dataclass(frozen=True)
class Connection:
    nodes: List[Node]
    capacity: int
