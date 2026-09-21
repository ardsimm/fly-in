from collections import deque
from typing import Dict, List, Set

from src.models.map import Map
from src.models.node import Node
from src.simulation.simulation_exceptions import PathNotFoundError

PrevDict = Dict[Node, Node]


class Simulation:

    def __get_next_nodes(self, node: Node) -> List[Node]:
        next_nodes: List[Node] = []
        for connection in node.connections:
            next_node = next(
                iter(
                    [
                        connected_node
                        for connected_node in connection.nodes
                        if node != connected_node
                    ]
                ),
                None,
            )
            if next_node is not None:
                next_nodes.append(next_node)
        return next_nodes

    def bfs(self, node_from: Node, node_to: Node) -> List[Node]:
        visited: Set[Node] = set()
        queue: deque[Node] = deque()
        result: List[Node] = []
        prev_nodes: PrevDict = {}

        queue.append(node_from)
        visited.add(node_from)

        while queue:
            current = queue.popleft()
            next_nodes = [
                next_node
                for next_node in self.__get_next_nodes(current)
                if next_node not in visited
            ]
            if not len(next_nodes):
                continue
            for next_node in next_nodes:
                visited.add(next_node)
                prev_nodes[next_node] = current
                if next_node == node_to:
                    break
                queue.append(next_node)

        current = node_to
        while current and current != node_from:
            prev_node = prev_nodes.get(current)
            if not prev_node:
                raise PathNotFoundError(
                    f"No path found for node {node_to.name}"
                )
            result.append(prev_node)
            current = prev_node
        result.reverse()

        return result

    def check_solvable(self, map: Map) -> None:
        _ = self.bfs(map.entry_point, map.exit_point)
