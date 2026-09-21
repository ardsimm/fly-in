from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.models.connection import Connection


class Node:
    name: str
    color: str
    x: int
    y: int
    max_drones: int
    priority: int
    connections: List[Connection]
    drones_count: int

    def __init__(
        self,
        name: str,
        color: str,
        x: int,
        y: int,
        max_drones: int,
        priority: int,
        connections: List[Connection],
    ) -> None:
        self.name = name
        self.color = color
        self.x = x
        self.y = y
        self.max_drones = max_drones
        self.priority = priority
        self.connections = connections
        self.drones_count = 0

    def __repr__(self) -> str:
        return f"Node(name={
            self.name
        }, x={
            self.x
        }, y={
            self.y
        }, max_drones={
            self.max_drones
        }, priority={
            self.priority
        }, connections={
            [
                f'{connection.nodes[0].name}-{connection.nodes[1].name}'
                for connection in self.connections
            ]
        })"
