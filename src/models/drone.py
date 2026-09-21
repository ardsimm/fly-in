from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from typing_extensions import override

if TYPE_CHECKING:
    from src.models.node import Node


@dataclass
class Drone:
    path: List[Node]
    id: int
    name: str
    done: bool = False

    @override
    def __hash__(self) -> int:
        return hash(self.id)
