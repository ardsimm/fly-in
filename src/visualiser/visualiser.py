import sys
from math import floor
from traceback import print_exception
from typing import List, Optional

import pygame

from src.models import Map
from src.visualiser.color_palette import ColorPaletteTypedDict
from src.visualiser.elements.connection_element import ConnectionElement
from src.visualiser.elements.drone_element import DroneElement
from src.visualiser.elements.element import Element
from src.visualiser.elements.node_element import NodeElement
from src.visualiser.managers.mouse_manager import MouseManager


class Visualiser:

    map: Map
    screen: pygame.Surface
    colors: ColorPaletteTypedDict
    window_width: int
    window_height: int
    node_bounding_rect_size: int
    target_fps: int
    elements: List[Element]
    mouse_manager: MouseManager

    def __compute_node_bounding_rect(self) -> int:
        max_x = max(self.map.nodes, key=lambda node: node.x).x
        max_y = max(self.map.nodes, key=lambda node: node.y).y
        max_coord = max(max_x, max_y)
        return floor(
            min(self.window_width, self.window_height) / (max_coord + 1)
        )

    def __init__(
        self,
        map: Map,
        color_palette: ColorPaletteTypedDict = {},
        window_width: Optional[int] = None,
        window_height: Optional[int] = None,
        target_fps: int = 60,
    ) -> None:
        _ = pygame.init()
        if window_height is None:
            window_height = floor(pygame.display.Info().current_h * 4 / 5)
        if window_width is None:
            window_width = floor(pygame.display.Info().current_w * 4 / 5)

        self.map = map
        self.colors = color_palette
        self.window_width = window_width
        self.window_height = window_height
        self.target_fps = target_fps
        self.node_bounding_rect_size = self.__compute_node_bounding_rect()
        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height)
        )
        self.elements = []
        pygame.display.set_caption("fly-in")
        self.mouse_manager = MouseManager.get_instance()

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
                    elif event.type == pygame.MOUSEMOTION:
                        self.mouse_manager.cursor_position = (
                            pygame.mouse.get_pos()
                        )

                _ = self.screen.fill((39, 43, 48))

                self.__draw_elements()

                pygame.display.flip()

                self.__update_elements(dt, combined_dt)

                dt = clock.tick(self.target_fps)
                combined_dt += dt

        except BaseException as e:
            print(f"An unhandled excetion occured:\n{e}", file=sys.stderr)
            print_exception(e)
            pygame.quit()
            return 1

        pygame.quit()
        return 0
