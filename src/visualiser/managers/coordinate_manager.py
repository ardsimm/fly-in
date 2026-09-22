from math import floor
from typing import Tuple

from src.models.node import Node


class CoordinateManager:
    @staticmethod
    def get_node_real_coordinate(
        node: Node, node_bounding_rect_size: int
    ) -> Tuple[int, int]:
        real_x = floor(
            node.x * node_bounding_rect_size + node_bounding_rect_size / 2
        )

        real_y = floor(
            node.y * node_bounding_rect_size + node_bounding_rect_size / 2
        )

        return (real_x, real_y)

    @staticmethod
    def get_paddings(
        max_x: int,
        max_y: int,
        node_bounding_rect_size: int,
    ) -> Tuple[int, int]:
        padding_x = 0
        padding_y = 0
        max_coord = max(max_x, max_y)
        if max_coord == max_x:
            coord_delta = max_x - max_y
            padding_y = floor(node_bounding_rect_size * coord_delta / 2)
        else:
            coord_delta = max_y - max_x
            padding_x = floor(node_bounding_rect_size * coord_delta / 2)

        return (padding_x, padding_y)
