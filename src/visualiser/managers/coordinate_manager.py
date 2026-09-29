from math import floor
from typing import Tuple


class CoordinateManager:
    """Convert map coordinates to screen coordinates."""

    @staticmethod
    def get_node_real_coordinate(
        x: float, y: float, node_bounding_rect_size: int
    ) -> Tuple[int, int]:
        """Convert map coordinates to the pixel center of their cell.

        Args:
            x: X coordinate on the map.
            y: Y coordinate on the map.
            node_bounding_rect_size: Size of one map unit, in pixels.

        Returns:
            The pixel coordinates, without padding.
        """
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
        """Compute the offsets that center the map in the window.

        Args:
            max_x: Maximum x coordinate of the map.
            max_y: Maximum y coordinate of the map.
            node_bounding_rect_size: Size of one map unit, in pixels.
            window_height: Window height, in pixels.
            window_width: Window width, in pixels.

        Returns:
            The x and y offsets, in pixels.
        """
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
