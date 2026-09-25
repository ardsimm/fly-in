from enum import Enum


class NodePriority(Enum):
    blocked = -1
    restricted = 0
    normal = 1
    priority = 2
