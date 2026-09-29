from enum import Enum


class NodePriority(Enum):
    """Zone types, stored as Node.priority.

    Higher values are preferred by the pathfinding. Blocked zones are never
    entered, restricted zones take two turns to reach.
    """

    blocked = -1
    restricted = 0
    normal = 1
    priority = 2
