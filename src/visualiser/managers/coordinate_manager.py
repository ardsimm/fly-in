from math import floor
from typing import Tuple


class CoordinateManager:
    @staticmethod
    def get_node_real_coordinate(
        x: float, y: float, node_bounding_rect_size: int
    ) -> Tuple[int, int]:
        real_x = floor(
            x * node_bounding_rect_size + node_bounding_rect_size / 2
        )

        real_y = floor(
            y * node_bounding_rect_size + node_bounding_rect_size / 2
        )

        return (real_x, real_y)

    @staticmethod
    def get_paddings(
        max_x: int,
        max_y: int,
        node_bounding_rect_size: int,
        window_height: int,
        window_width: int,
    ) -> Tuple[int, int]:
        padding_x = 0
        padding_y = 0
        if max_x * node_bounding_rect_size != window_width:
            coord_delta = floor(window_height / node_bounding_rect_size) - (
                max_y + 1
            )
            padding_y = floor(node_bounding_rect_size * coord_delta / 2)
        if max_y * node_bounding_rect_size != window_height:
            coord_delta = floor(window_width / node_bounding_rect_size) - (
                max_x + 1
            )
            padding_x = floor(node_bounding_rect_size * coord_delta / 2)

        return (padding_x, padding_y)
