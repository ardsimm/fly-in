from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Union

from typing_extensions import override

from src.models.connection import Connection

if TYPE_CHECKING:
    from src.models.node import Node


@dataclass
class Drone:
    path: List[Union[Node, Connection]]
    id: int
    name: str
    done: bool = False

    @override
    def __hash__(self) -> int:
        return hash(self.id)
