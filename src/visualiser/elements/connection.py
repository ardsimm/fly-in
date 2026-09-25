import pygame
from typing_extensions import final, override

from src.models.connection import Connection
from src.visualiser.elements.element import Element
from src.visualiser.managers.color_manager import ColorManager
from src.visualiser.managers.coordinate_manager import CoordinateManager


@final
class ConnectionElement(Element):

    screen: pygame.Surface
    connection: Connection
    max_x: int
    max_y: int
    node_bounding_rect_size: int

    def __init__(
        self,
        screen: pygame.Surface,
        connection: Connection,
        max_x: int,
        max_y: int,
        node_bounding_rect_size: int,
    ) -> None:
        super().__init__()
        self.screen = screen
        self.connection = connection
        self.max_x = max_x
        self.max_y = max_y
        self.node_bounding_rect_size = node_bounding_rect_size
        self.z_index = 1

    @override
    def draw(self) -> None:
        node_from = self.connection.nodes[0]
        node_to = self.connection.no[1]
        padding_x, padding_y = CoordinateManager.get_paddings(
            self.max_x,
            self.max_y,
            self.node_bounding_rect_size,
            self.screen.height,
            self.screen.width
        )

        from_x, from_y = CoordinateManager.get_node_real_coordinate(
            node_from.x, node_from.y, self.node_bounding_rect_size
        )
        from_x += padding_x
        from_y += padding_y

        to_x, to_y = CoordinateManager.get_node_real_coordinate(
            node_to.x, node_to.y, self.node_bounding_rect_size
        )
        to_x += padding_x
        to_y += padding_y

        _ = pygame.draw.line(
            self.screen,
            ColorManager.get_color_in_rgb("blue"),
            (from_x, from_y),
            (to_x, to_y),
            width=3,
        )
