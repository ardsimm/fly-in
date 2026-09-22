from math import floor

import pygame
from typing_extensions import final, override

from src.models.node import Node
from src.visualiser.managers.color_manager import ColorManager
from src.visualiser.managers.coordinate_manager import CoordinateManager

from .element import Element


@final
class NodeElement(Element):

    screen: pygame.Surface
    node_bounding_rect_size: int
    max_x: int
    max_y: int
    node: Node

    def __init__(
        self,
        screen: pygame.Surface,
        node_bounding_rect_size: int,
        max_x: int,
        max_y: int,
        node: Node,
    ) -> None:
        super().__init__()
        self.screen = screen
        self.node_bounding_rect_size = node_bounding_rect_size
        self.max_x = max_x
        self.max_y = max_y
        self.node = node
        self.z_index = 2

    @override
    def draw(self) -> None:
        padding_x = 0
        padding_y = 0
        padding_x, padding_y = CoordinateManager.get_paddings(
            self.max_x, self.max_y, self.node_bounding_rect_size
        )
        node_radius = floor(self.node_bounding_rect_size / 4)

        circle_x, circle_y = CoordinateManager.get_node_real_coordinate(
            self.node.x, self.node.y, self.node_bounding_rect_size
        )
        circle_x += padding_x
        circle_y += padding_y

        _ = pygame.draw.aacircle(
            self.screen,
            (250, 250, 250),
            pygame.Vector2(circle_x, circle_y),
            node_radius,
        )

        _ = pygame.draw.aacircle(
            self.screen,
            ColorManager.get_color(self.node.color),
            pygame.Vector2(circle_x, circle_y),
            node_radius - 5,
        )
