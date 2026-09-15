from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.models.connection import Connection


@dataclass(frozen=True)
class Node:
    name: str
    color: str
    x: int
    y: int
    max_drones: int
    priority: int
    connections: List[Connection]
