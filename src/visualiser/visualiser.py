import sys
from math import floor
from typing import List, Tuple

import pygame
from matplotlib import colors

from src.models import Connection, Map, Node
from src.visualiser.color_palette import ColorPaletteTypedDict


class Visualiser:

    map: Map
    screen: pygame.Surface
    colors: ColorPaletteTypedDict
    window_width: int
    window_height: int
    node_bounding_rect_size: int
    target_fps: int

    def __compute_node_bounding_rect(self) -> int:
        max_x = max(self.map.nodes, key=lambda node: node.x).x
        max_y = max(self.map.nodes, key=lambda node: node.y).y
        max_coord = max(max_x, max_y)
        return floor(
            max(self.window_width, self.window_height) / (max_coord + 1)
        )

    def __init__(
        self,
        map: Map,
        color_palette: ColorPaletteTypedDict = {},
        window_width: int = 1000,
        window_height: int = 1000,
        target_fps: int = 60,
    ) -> None:
        self.map = map
        self.colors = color_palette
        self.window_width = window_width
        self.window_height = window_height
        self.target_fps = target_fps
        self.node_bounding_rect_size = self.__compute_node_bounding_rect()
        _ = pygame.init()
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height)
        )

    def __get_node_real_coordinate(self, node: Node) -> Tuple[int, int]:
        real_x = floor(
            node.x * self.node_bounding_rect_size
            + self.node_bounding_rect_size / 2
        )

        real_y = floor(
            node.y * self.node_bounding_rect_size
            + self.node_bounding_rect_size / 2
        )

        return (real_x, real_y)

    def __get_paddings(self, max_x: int, max_y: int) -> Tuple[int, int]:
        padding_x = 0
        padding_y = 0
        max_coord = max(max_x, max_y)
        if max_coord == max_x:
            coord_delta = max_x - max_y
            padding_y = floor(self.node_bounding_rect_size * coord_delta / 2)
        else:
            coord_delta = max_y - max_x
            padding_x = floor(self.node_bounding_rect_size * coord_delta / 2)

        return (padding_x, padding_y)

    def __get_color_in_rgb(self, color: str) -> Tuple[int, int, int]:
        try:
            r, g, b = colors.to_rgb(color)
        except ValueError:
            print(f"Waning: unknown color {color}, defaulting to black.")
            color = "red"
            r, g, b = colors.to_rgb(color)
        return (floor(r * 255), floor(g * 255), floor(b * 255))

    def __draw_connections(
        self, connections: List[Connection], nodes: List[Node]
    ) -> None:
        for connection in connections:
            node_from = connection.nodes[0]
            node_to = connection.nodes[1]
            max_x = max(nodes, key=lambda node: node.x).x
            max_y = max(nodes, key=lambda node: node.y).y
            padding_x, padding_y = self.__get_paddings(max_x, max_y)

            from_x, from_y = self.__get_node_real_coordinate(node_from)
            from_x += padding_x
            from_y += padding_y

            to_x, to_y = self.__get_node_real_coordinate(node_to)
            to_x += padding_x
            to_y += padding_y

            _ = pygame.draw.line(
                self.screen,
                self.__get_color_in_rgb("blue"),
                (from_x, from_y),
                (to_x, to_y),
                width=3,
            )

    def __draw_nodes(self, nodes: List[Node]) -> None:
        padding_x = 0
        padding_y = 0
        max_x = max(nodes, key=lambda node: node.x).x
        max_y = max(nodes, key=lambda node: node.y).y
        padding_x, padding_y = self.__get_paddings(max_x, max_y)
        node_radius = floor(self.node_bounding_rect_size / 4)

        for node in nodes:

            circle_x, circle_y = self.__get_node_real_coordinate(node)
            circle_x += padding_x
            circle_y += padding_y

            _ = pygame.draw.circle(
                self.screen,
                self.__get_color_in_rgb(node.color),
                pygame.Vector2(circle_x, circle_y),
                node_radius,
            )

    def __draw_map(self, map: Map) -> None:
        self.__draw_connections(map.connections, map.nodes)
        self.__draw_nodes(map.nodes)

    def render(self) -> int:
        clock = pygame.time.Clock()
        running = True

        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYUP and event.key == pygame.K_q
                    ):
                        running = False

                _ = self.screen.fill("white")

                self.__draw_map(self.map)

                pygame.display.flip()

                _ = clock.tick(self.target_fps)
        except BaseException as e:
            print(f"An unhandled excetion occured:\n{e}", file=sys.stderr)
            pygame.quit()
            return 1

        pygame.quit()
        return 0
