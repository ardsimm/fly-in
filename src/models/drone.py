from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import override


@dataclass
class Drone:
    id: int
    name: str
    done: bool = False

    @override
    def __hash__(self) -> int:
        return hash(self.id)

    @override
    def __str__(self) -> str:
        return f"D{self.id}"
