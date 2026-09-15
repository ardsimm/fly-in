import sys
from math import floor
from traceback import print_exception
from typing import List, Tuple
from matplotlib import colors

import pygame

from src.models import Map, Node
from src.visualiser.color_palette import ColorPaletteTypedDict


class Visualiser:

    map: Map
    screen: pygame.Surface
    colors: ColorPaletteTypedDict
    window_width: int
    window_height: int
    target_fps: int

    def __init__(
        self,
        map: Map,
        color_palette: ColorPaletteTypedDict = {},
        window_width: int = 800,
        window_height: int = 800,
        target_fps: int = 60
    ) -> None:
        self.map = map
        self.colors = color_palette
        self.window_width = window_width
        self.window_height = window_height
        self.target_fps = target_fps
        _ = pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))

    def __draw_nodes(self, nodes: List[Node]) -> None:
        print("======================================")
        print("========== drawing nodes... ==========")
        print("======================================")
        padding_x = 0
        padding_y = 0
        print("nodes len:", len(nodes))
        max_x = max(nodes, key=lambda node: node.x).x
        print("max_x:", max_x)
        max_y = max(nodes, key=lambda node: node.y).y
        print("max_y:", max_y)
        max_coord = max(max_x, max_y)
        print("max_coord:", max_coord)
        node_bounding_rect_size = (
            max(self.window_width, self.window_height)
            / (max_coord + 1)
        )
        if max_coord == max_x:
            coord_delta = max_x - max_y
            padding_y = (
                node_bounding_rect_size
                * coord_delta / 2
            )
        else:
            coord_delta = max_y - max_x
            padding_x = (
                node_bounding_rect_size
                * coord_delta / 2
            )
        print("padding_x:", padding_x)
        print("padding_y:", padding_y)
        print("window_width:", self.window_width)
        print("window_height:", self.window_height)
        print("node_bounding_rect_size:", node_bounding_rect_size)
        node_radius = floor(node_bounding_rect_size / 4)
        print("node_radius:", node_radius)

        for node in nodes:
            print("---------- drawing node... ----------")

            print("node.x:", node.x)
            circle_x = floor(
                node.x
                * node_bounding_rect_size
                + node_bounding_rect_size / 2
                + padding_x
            )
            print("circle_x:", circle_x)

            print("node.y:", node.y)
            circle_y = floor(
                node.y
                * node_bounding_rect_size
                + node_bounding_rect_size / 2
                + padding_y
            )
            print("circle_y:", circle_y)

            try:
                (r, g, b, _) = colors.to_rgba(node.color)
            except ValueError:
                print(
                    f"Waning: unknown color {node.color}, defaulting to black."
                )
                node.color = "black"
                (r, g, b, _) = colors.to_rgba(node.color)

            _ = pygame.draw.circle(
                self.screen,
                (floor(r), floor(g), floor(b)),
                pygame.Vector2(circle_x, circle_y),
                node_radius
            )

    def __draw_map(self, map: Map) -> None:
        self.__draw_nodes(map.nodes)

    def render(self) -> int:
        clock = pygame.time.Clock()
        running = True

        try:
            while running:
                for event in pygame.event.get():
                    if (
                        event.type == pygame.QUIT
                        or (
                            event.type == pygame.KEYUP
                            and event.key == pygame.K_q
                        )
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
