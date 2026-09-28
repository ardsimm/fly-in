from collections import deque
from heapq import heappop, heappush
from typing import Dict, List, Optional, Set, Tuple, Union

from src.enums.node_priority import NodePriority
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
    Tuple[Optional[Node], Optional[Connection]],
]

CooperativePrevDictValue = Tuple[
    Tuple[Optional[Node], Optional[Connection]], Optional[Connection]
]

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
                and next_node.priority != NodePriority.blocked.value
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

    def cooperative_bfs(
        self, map: Map
    ) -> Dict[Drone, List[Union[Node, Connection]]]:
        paths: Dict[Drone, List[Union[Node, Connection]]] = {}
        allocation_table: Dict[int, Dict[Union[Node, Connection], int]] = {}

        turn = 0
        for drone in map.drones:
            queue: List[
                Tuple[
                    int,
                    int,
                    Optional[Node],
                    Tuple[Optional[Connection], Optional[Node]],
                ]
            ] = [(0, 0, map.entry_point, (None, None))]
            visited: Set[Node] = {map.entry_point}
            prev_nodes: Dict[
                Tuple[int, Union[Node, Connection]],
                Tuple[Union[Node, Connection], Optional[Connection]],
            ] = {}
            end_turn = 0
            insertion_idx = 1

            while not drone.done and queue:

                turn, _, current, (transit_connection, transit_destination) = (
                    heappop(queue)
                )

                next_turn_allocation_table = allocation_table.setdefault(
                    turn + 1, ({})
                )
                turn_allocation_table = allocation_table.setdefault(turn, ({}))

                can_wait = False
                all_visited = True
                if current:
                    current.connections.sort(
                        key=lambda connection: -next(
                            iter(
                                connected_node
                                for connected_node in connection.nodes
                                if connected_node != current
                            )
                        ).priority
                    )

                    for connection in current.connections:

                        if connection == transit_connection:
                            continue

                        next_node = next(
                            iter(
                                connected_node
                                for connected_node in connection.nodes
                                if connected_node != current
                            )
                        )

                        connection_occupency = (
                            turn_allocation_table.setdefault(connection, 0)
                        )
                        connection_capacity = connection.capacity
                        next_node_occupency = (
                            next_turn_allocation_table.setdefault(next_node, 0)
                        )

                        if next_node == map.exit_point:
                            next_node_capacity = connection.capacity
                        else:
                            next_node_capacity = next_node.max_drones

                        all_visited &= next_node in visited
                        if (
                            next_node in visited
                            or next_node.priority == NodePriority.blocked.value
                            or connection_occupency >= connection_capacity
                            or next_node_occupency >= next_node_capacity
                        ):
                            can_wait = True
                            continue

                        if next_node.priority != NodePriority.restricted.value:
                            visited.add(next_node)
                            prev_nodes[(turn, next_node)] = (
                                current,
                                connection,
                            )
                            insertion_idx += 1
                            heappush(
                                queue,
                                (
                                    turn + 1,
                                    insertion_idx,
                                    next_node,
                                    (None, None),
                                ),
                            )
                            if next_node == map.exit_point:
                                drone.done = True
                                break
                        else:
                            restricted_node_occupency = (
                                allocation_table.setdefault(
                                    turn + 2, {}
                                ).setdefault(next_node, 0)
                            )

                            if (
                                restricted_node_occupency
                                >= next_node.max_drones
                            ):
                                can_wait = True
                                continue

                            prev_nodes[(turn, connection)] = (
                                current,
                                connection,
                            )
                            insertion_idx += 1
                            heappush(
                                queue,
                                (
                                    turn + 1,
                                    insertion_idx,
                                    None,
                                    (connection, next_node),
                                ),
                            )
                            heappush(
                                queue,
                                (
                                    turn + 2,
                                    insertion_idx,
                                    next_node,
                                    (None, None),
                                ),
                            )
                            visited.add(next_node)

                elif transit_connection:
                    assert transit_destination is not None
                    next_node = transit_destination
                    prev_nodes[(turn, next_node)] = (transit_connection, None)
                    if transit_destination == map.exit_point:
                        drone.done = True
                if (
                    can_wait
                    and not all_visited
                    and current
                    and (
                        current == map.exit_point
                        or current == map.entry_point
                        or len(current.connections) > 1
                    )
                ):
                    prev_nodes[(turn, current)] = (
                        current,
                        None,
                    )
                    insertion_idx += 1
                    heappush(
                        queue, (turn + 1, insertion_idx, current, (None, None))
                    )

                end_turn = turn

            paths[drone] = []

            turn = end_turn
            current_step: Optional[Union[Node, Connection]] = map.exit_point
            current_connection: Optional[Connection] = None
            while current_step:

                paths[drone].append(current_step)

                current_step, current_connection = prev_nodes.get(
                    (turn, current_step)
                ) or (
                    None,
                    None,
                )

                if (
                    current_step is None
                    and map.entry_point not in paths[drone]
                ):
                    raise PathNotFoundError("Path not found")

                if current_step is not None:
                    _ = allocation_table[turn].setdefault(current_step, 0)
                    allocation_table[turn][current_step] += 1

                if current_connection is not None:
                    _ = allocation_table[turn].setdefault(
                        current_connection, 0
                    )
                    allocation_table[turn][current_connection] += 1

                turn -= 1

            paths[drone].reverse()
            drone.path = paths[drone]

        return paths

    def get_turns(
        self, map: Map, paths: Dict[Drone, List[Union[Node, Connection]]]
    ) -> List[List[Tuple[Drone, Union[Connection, Node]]]]:
        occupency_table: Dict[Union[Node, Connection], int] = {}

        turns: List[List[Tuple[Drone, Union[Connection, Node]]]] = []
        max_path_len = max([len(path) for path in paths.values()])

        for i in range(max_path_len):
            turn: List[Tuple[Drone, Union[Connection, Node]]] = []
            for drone, path in paths.items():

                if i >= len(path):
                    continue

                current_step = path[i]
                previous_step: Optional[Union[Node, Connection]] = None

                if i > 0:
                    previous_step = path[i - 1]

                if previous_step != current_step:

                    if previous_step:
                        occupency_table[previous_step] -= 1
                    _ = occupency_table.setdefault(current_step, 0)

                    occupency_table[current_step] += 1
                    current_step_capacity = 0

                    if isinstance(current_step, Node):
                        current_step_capacity = current_step.max_drones
                    else:
                        current_step_capacity = current_step.capacity

                    if (
                        current_step not in [map.entry_point, map.exit_point]
                        and occupency_table[current_step]
                        > current_step_capacity
                    ):
                        raise InvalidMoveError(f"invalid move D{
                                drone.id
                        }:{
                            current_step
                        }: exceeds capacity"
                        )

                    if isinstance(current_step, Node):
                        if (
                            current_step.priority
                            == NodePriority.restricted.value
                            and not isinstance(previous_step, Connection)
                        ):
                            raise InvalidMoveError(
                                f"Invalid move D{
                                    drone.id
                                }:{
                                    current_step
                                }: node is restricted and previous"
                                + " step wasn't a connection"
                            )
                        if current_step.priority == NodePriority.blocked.value:
                            raise InvalidMoveError(
                                f"Invalid move D{
                                    drone.id
                                }:{
                                    current_step
                                }: node is blocked"
                            )
                    else:
                        if isinstance(previous_step, Connection):
                            raise InvalidMoveError(
                                f"Invalid move D{
                                    drone.id
                                }:{
                                    current_step
                                }: waiting on a connection"
                            )

                    turn.append((drone, path[i]))
            turns.append(turn)
        return turns

    def print_turns(
        self, turns: List[List[Tuple[Drone, Union[Connection, Node]]]]
    ) -> None:
        for turn in turns:
            for drone, step in turn:
                print(drone, step, sep="-", end=" ")
            print()

    def check_solvable(self, map: Map) -> None:
        _ = self.bfs(map.entry_point, map.exit_point)
