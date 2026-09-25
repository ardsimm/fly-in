from collections import deque
from typing import Dict, List, Optional, Set, Tuple

from src.models.connection import Connection
from src.models.drone import Drone
from src.models.map import Map
from src.models.node import Node
from src.simulation.simulation_exceptions import (
    InvalidMoveError,
    PathNotFoundError,
)

PrevDict = Dict[Node, Node]

CooperativePrevDictKey = Tuple[
    int,
    Node,
]

CooperativePrevDictValue = Tuple[Node, Optional[Connection]]

CooperativePrevDict = Dict[CooperativePrevDictKey, CooperativePrevDictValue]


class Simulation:
    def __get_next_nodes(
        self, node: Node, available_connections: List[Connection]
    ) -> List[Node]:
        next_nodes: List[Node] = []
        for connection in available_connections:
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

    def bfs(
        self,
        node_from: Node,
        node_to: Node,
        visited: Optional[Set[Node]] = None,
    ) -> List[Node]:
        queue: deque[Node] = deque()
        result: List[Node] = []
        prev_nodes: PrevDict = {}

        queue.append(node_from)
        if not visited:
            visited = {node_from}

        while queue:
            current = queue.popleft()
            next_nodes = [
                next_node
                for next_node in self.__get_next_nodes(
                    current, current.connections
                )
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
            if prev_node:
                print(prev_node.name)
            else:
                print("[None]")
            if not prev_node:
                raise PathNotFoundError(
                    f"No path found for node {node_to.name}"
                )
            result.append(prev_node)
            current = prev_node
        result.reverse()
        result.append(node_to)
        return result

    def cooperative_bfs(self, map: Map) -> Dict[Drone, List[Node]]:
        paths: Dict[Drone, List[Node]] = {}
        allocation_table: Dict[
            int, Tuple[Dict[Node, int], Dict[Connection, int]]
        ] = {}

        turn = 0
        for drone in map.drones:
            queue: deque[Tuple[int, Node]] = deque([(0, map.entry_point)])
            visited: Set[Node] = {map.entry_point}
            prev_nodes: CooperativePrevDict = {}
            end_turn = 0

            print(f"=========== Computing D{drone.id} ===========")
            while not drone.done and queue:

                turn, current_node = queue.popleft()
                # print("Visited", current_node)

                if current_node == map.exit_point:
                    break

                next_turn_allocation_table = allocation_table.setdefault(
                    turn + 1, ({}, {})
                )
                turn_allocation_table = allocation_table.setdefault(
                    turn, ({}, {})
                )

                current_node.connections.sort(
                    key=lambda connection: -next(
                        iter(
                            connected_node
                            for connected_node in connection.nodes
                            if connected_node != current_node
                        )
                    ).priority
                )

                can_wait = False
                all_visited = True
                for connection in current_node.connections:

                    next_node = next(
                        iter(
                            connected_node
                            for connected_node in connection.nodes
                            if connected_node != current_node
                        )
                    )

                    connection_occupency = turn_allocation_table[1].setdefault(
                        connection, 0
                    )
                    connection_capacity = connection.capacity
                    next_node_occupency = next_turn_allocation_table[
                        0
                    ].setdefault(next_node, 0)
                    if next_node == map.exit_point:
                        next_node_capacity = connection.capacity
                    else:
                        next_node_capacity = next_node.max_drones

                    all_visited &= next_node in visited
                    if (
                        next_node in visited
                        or connection_occupency >= connection_capacity
                        or next_node_occupency >= next_node_capacity
                    ):
                        can_wait = True
                        continue

                    visited.add(next_node)
                    prev_nodes[(turn, next_node)] = (current_node, connection)
                    queue.append((turn + 1, next_node))
                    if next_node == map.exit_point:
                        drone.done = True
                        break

                if (
                    can_wait
                    and not all_visited
                    and (
                        current_node == map.exit_point
                        or current_node == map.entry_point
                        or len(current_node.connections) > 1
                    )
                ):
                    print("At turn", turn, "waiting on", current_node.name)
                    prev_nodes[(turn, current_node)] = (current_node, None)
                    queue.append((turn + 1, current_node))

                end_turn = turn

            paths[drone] = []

            print("------ Allocation table ------")
            for turn, turn_allocation_table in allocation_table.items():
                print(f"Turn {turn}:")
                for node, node_occupency in turn_allocation_table[0].items():
                    print(f"Node {node.name}: {node_occupency}")
                for connection, connection_occupency in turn_allocation_table[
                    1
                ].items():
                    print(
                        f"Connection {
                            connection.nodes[0].name}-{connection.nodes[1].name
                        }: {connection_occupency}"
                    )

            print("------ Previous nodes ------")
            for key, turn_allocation_table in prev_nodes.items():
                print(
                    f"{key[0]}: {turn_allocation_table[0].name}->{key[1].name}"
                )

            print("------ Reconstructing path ------")
            turn = end_turn
            current: Optional[Node] = map.exit_point
            connection: Optional[Connection] = None
            while current:

                print("Node:", turn, ":", current.name)

                paths[drone].append(current)

                current, connection = prev_nodes.get((turn, current)) or (
                    None,
                    None,
                )
                if current is None and map.entry_point not in paths[drone]:
                    raise PathNotFoundError("Path not found")

                if current is not None:
                    _ = allocation_table[turn][0].setdefault(current, 0)
                    allocation_table[turn][0][current] += 1

                if connection is not None:
                    _ = allocation_table[turn][1].setdefault(connection, 0)
                    allocation_table[turn][1][connection] += 1

                turn -= 1

            paths[drone].reverse()
            drone.path = paths[drone]

            print(drone.id)
            print([node.name for node in drone.path])

        return paths

    def get_turns(
        self, map: Map, paths: Dict[Drone, List[Node]]
    ) -> List[List[Tuple[Drone, Node, int]]]:
        nodes_occupency: Dict[int, Dict[Node, int]] = {}
        max_turn = max([len(path) for path in paths.values()])
        turns: List[List[Tuple[Drone, Node, int]]] = []
        for i in range(max_turn):
            print(f"----- Turn {i} -----")
            turn: List[Tuple[Drone, Node, int]] = []
            for drone, path in paths.items():
                if i >= len(path):
                    continue
                current_node = path[i]

                _ = nodes_occupency.setdefault(i, {}).setdefault(
                    current_node, 0
                )
                nodes_occupency[i][current_node] += 1

                if i > 0:
                    nodes_occupency[i - 1][path[i - 1]] -= 1

                step = (drone, path[i], nodes_occupency[i][current_node])
                print(f"D{step[0].id}:{step[1].name} ({step[2]} drones)")
                if (
                    current_node != map.entry_point
                    and current_node != map.exit_point
                    and nodes_occupency[i][current_node]
                    > current_node.max_drones
                ):
                    raise InvalidMoveError(f"Invalid move D{drone.id}->{
                        current_node.name
                    }(capacity:{current_node.max_drones}, occupency: {
                        nodes_occupency[i][current_node]
                    })")

                turn.append(step)
            turns.append(turn)
        return turns

    def check_solvable(self, map: Map) -> None:
        _ = self.bfs(map.entry_point, map.exit_point)
