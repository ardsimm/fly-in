from collections import deque
from typing import Dict, List, Set

from src.models.map import Map
from src.models.node import Node
from src.simulation.simulation_exceptions import PathNotFoundError

PrevDict = Dict[Node, Node]

class Simulation:

    def bfs(self, node_from: Node, node_to: Node) -> List[Node]:
        visited: Set[Node] = set()
        queue: deque[Node] = deque()
        result: List[Node] = []
        prev_nodes: PrevDict = {}

        queue.append(node_from)
        visited.add(node_from)

        while queue:
            current = queue.popleft()
            for connection in current.connections:
                node = next(
                    iter([
                        node
                        for node in connection.nodes
                        if node != current
                        and current not in visited
                    ]), None
                )
                if node is None:
                    continue
                visited.add(node)
                prev_nodes[node] = current
                if node == node_to:
                    break
                queue.append(node)

            current = node_to
            while current:
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