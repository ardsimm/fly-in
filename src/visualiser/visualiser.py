import sys
from math import floor
from typing import List

import pygame

from src.models import Map
from src.visualiser.color_palette import ColorPaletteTypedDict
from src.visualiser.elements.connection_element import ConnectionElement
from src.visualiser.elements.drone_element import DroneElement
from src.visualiser.elements.element import Element
from src.visualiser.elements.node_element import NodeElement


class Visualiser:

    map: Map
    screen: pygame.Surface
    colors: ColorPaletteTypedDict
    window_width: int
    window_height: int
    node_bounding_rect_size: int
    target_fps: int
    elements: List[Element]

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
        self.elements = []
        pygame.display.set_caption("fly-in")

    def __update_elements(self, dt: int, combined_dt: int) -> None:
        for element in self.elements:
            element.update(dt, combined_dt)

    def __draw_elements(self) -> None:
        for element in self.elements:
            element.draw()

    def __init_elements(self) -> None:
        max_x = max(self.map.nodes, key=lambda node: node.x).x
        max_y = max(self.map.nodes, key=lambda node: node.y).y

        for node in self.map.nodes:
            self.elements.append(
                NodeElement(
                    screen=self.screen,
                    node_bounding_rect_size=self.node_bounding_rect_size,
                    max_x=max_x,
                    max_y=max_y,
                    node=node,
                )
            )

        for connection in self.map.connections:
            self.elements.append(
                ConnectionElement(
                    connection=connection,
                    max_x=max_x,
                    max_y=max_y,
                    node_bounding_rect_size=self.node_bounding_rect_size,
                    screen=self.screen,
                )
            )

        for drone in self.map.drones:
            self.elements.append(
                DroneElement(
                    drone=drone,
                    screen=self.screen,
                    max_x=max_x,
                    max_y=max_y,
                    node_bounding_rect_size=self.node_bounding_rect_size,
                )
            )

        self.elements.sort(key=lambda el: el.z_index)

    def render(self) -> int:
        clock = pygame.time.Clock()
        running = True
        self.__init_elements()
        combined_dt: int = 0
        dt: int = 0
        try:
            while running:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYUP and event.key == pygame.K_q
                    ):
                        running = False

                _ = self.screen.fill((39, 43, 48))

                self.__draw_elements()

                pygame.display.flip()

                self.__update_elements(dt, combined_dt)

                dt = clock.tick(self.target_fps)
                combined_dt += dt

        except BaseException as e:
            print(f"An unhandled excetion occured:\n{e}", file=sys.stderr)
            pygame.quit()
            return 1

        pygame.quit()
        return 0
