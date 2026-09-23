from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from src.models.drone import Drone
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
        result.append(node_to)
        return result

    def cooperative_bfs(self, map: Map) -> List[List[Tuple[Drone, Node]]]:
        claimed: Set[Tuple[int, Node]] = set()
        paths: Dict[Drone, List[Node]] = {}
        turns: List[List[Tuple[Drone, Node]]] = []

        turn = 0

        for drone in map.drones:
            queue: deque[Tuple[int, Node]] = deque([(0, map.entry_point)])
            visited: Set[Node] = {map.entry_point}
            prev_nodes: Dict[Tuple[int, Node], Node] = {}

            while not drone.done:
                turn, current_node = queue.popleft()

                if current_node == map.exit_point:
                    break
                next_nodes = self.__get_next_nodes(current_node)
                next_nodes.sort(key=lambda node: node.priority)

                must_wait = False
                next_node: Node
                for next_node in next_nodes:
                    if (turn, next_node) in claimed or next_node in visited:
                        must_wait = True
                        continue
                    visited.add(next_node)
                    print(
                        "At turn",
                        turn,
                        "visited",
                        next_node.name,
                        "comming from",
                        current_node.name,
                    )
                    prev_nodes[(turn, next_node)] = current_node
                    queue.append((turn + 1, next_node))
                    if next_node == map.exit_point:
                        drone.done = True
                        break

                if must_wait:
                    print("At turn", turn, "waiting on", current_node.name)

                    prev_nodes[(turn, current_node)] = current_node
                    queue.append((turn + 1, current_node))

            paths[drone] = []
            for key, value in prev_nodes.items():
                print(f"{key[0]}, {key[1].name}:{value.name}")

            current: Optional[Node] = map.exit_point
            while current:
                print("Turn:", turn, "Current:", current.name)
                if (
                    current is not None
                    and current not in (map.entry_point, map.exit_point)
                ):
                    claimed.add((turn, current))
                paths[drone].append(current)
                current = prev_nodes.get((turn, current))
                # if current is None and map.entry_point not in paths[drone]:
                #     raise PathNotFoundError("Path not found")
                turn -= 1
            paths[drone].reverse()
            drone.path = list(paths[drone])
            print(drone.id)
            print([node.name for node in drone.path])
        return turns

    def check_solvable(self, map: Map) -> None:
        _ = self.bfs(map.entry_point, map.exit_point)
