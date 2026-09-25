from math import floor
from typing import Tuple

import pygame
from typing_extensions import final, override

from src.models.node import Node
from src.visualiser.managers.color_manager import ColorManager
from src.visualiser.managers.coordinate_manager import CoordinateManager
from src.visualiser.managers.mouse_manager import MouseManager

from .element import Element


@final
class NodeElement(Element):

    screen: pygame.Surface
    node_bounding_rect_size: int
    max_x: int
    max_y: int
    node: Node
    hovered: bool
    node_radius: int

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
        self.hovered = False
        mouse_manager = MouseManager.get_instance()
        mouse_manager.mouse_move_subscribe(self, self.__class__.update_hovered)
        self.node_radius = floor(self.node_bounding_rect_size / 4)

    def update_hovered(self, mouse_pos: Tuple[int, int]) -> None:
        mouse_x, mouse_y = mouse_pos
        top_left = (
            self.node.x
            * self.node_bounding_rect_size,
            self.node.y
            * self.node_bounding_rect_size
        )
        bottom_right = (
            self.node.x * self.node_bounding_rect_size
            + self.node_bounding_rect_size,
            self.node.y * self.node_bounding_rect_size
            + self.node_bounding_rect_size
        )

        self.hovered = (
            mouse_x >= top_left[0]
            and mouse_y >= top_left[1]
            and mouse_x <= bottom_right[0]
            and mouse_y <= bottom_right[1]
        )

    @override
    def draw(self) -> None:
        padding_x = 0
        padding_y = 0
        padding_x, padding_y = CoordinateManager.get_paddings(
            self.max_x,
            self.max_y,
            self.node_bounding_rect_size,
            self.screen.height,
            self.screen.width,
        )

        circle_x, circle_y = CoordinateManager.get_node_real_coordinate(
            self.node.x, self.node.y, self.node_bounding_rect_size
        )
        circle_x += padding_x
        circle_y += padding_y

        _ = pygame.draw.aacircle(
            self.screen,
            (250, 250, 250),
            pygame.Vector2(circle_x, circle_y),
            self.node_radius,
        )

        _ = pygame.draw.aacircle(
            self.screen,
            ColorManager.get_color(self.node.color),
            pygame.Vector2(circle_x, circle_y),
            self.node_radius - 5,
        )

        font = pygame.font.Font(
            "freesansbold.ttf", floor(self.node_bounding_rect_size / 6)
        )

        if self.hovered:
            label_font_render = font.render(
                self.node.name, True, "white", None
            )
            label_rect = label_font_render.get_rect()
            label_rect.center = (circle_x, circle_y + self.node_radius * 2)
            _ = self.screen.blit(label_font_render, label_rect)

        max_drones_font_render = font.render(f"{
            self.node.max_drones
        }", True, "white", None)
        max_drones_rect = max_drones_font_render.get_rect()
        max_drones_rect.center = (circle_x, circle_y)
        _ = self.screen.blit(max_drones_font_render, max_drones_rect)
