from math import floor
from typing import Dict, List, Optional, Tuple, Union

import pygame
from typing_extensions import Literal

from src.models import Connection, Drone, Map
from src.models.node import Node
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
    drones: Dict[Drone, DroneElement]
    mouse_manager: MouseManager
    current_turn: int
    turns: List[List[Tuple[Drone, Union[Connection, Node]]]]
    auto_move: bool
    auto_move_delay: int

    def __compute_node_bounding_rect(self) -> int:
        max_x = max(self.map.nodes, key=lambda node: node.x).x
        max_y = max(self.map.nodes, key=lambda node: node.y).y
        width = self.window_width / (max_x + 1)
        height = self.window_height / (max_y + 1)
        if width < height:
            return max(floor(self.window_width / (max_x + 1)), 1)
        else:
            return max(floor(self.window_height / (max_y + 1)), 1)

    def __init__(
        self,
        map: Map,
        turns: List[List[Tuple[Drone, Union[Connection, Node]]]],
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
        self.current_turn = 0
        self.drones = {}
        self.turns = turns
        self.auto_move = False
        self.auto_move_delay = 500

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
            self.drones[drone] = DroneElement(
                map=self.map,
                drone=drone,
                max_x=max_x,
                max_y=max_y,
                node_bounding_rect_size=self.node_bounding_rect_size,
                screen=self.screen,
            )

        self.elements += self.drones.values()

        self.elements.sort(key=lambda el: el.z_index)

    def __get_animation_target(
        self, step: Union[Connection, Node]
    ) -> Tuple[float, float]:
        if isinstance(step, Node):
            return (step.x, step.y)
        else:
            return (
                (step.nodes[0].x + step.nodes[1].x) / 2,
                (step.nodes[0].y + step.nodes[1].y) / 2,
            )

    def progress_turn(self, direction: Literal[-1, 1]) -> None:
        next_turn = self.current_turn + direction
        if next_turn >= 0 and next_turn < len(self.turns):
            self.current_turn = next_turn
            current_turn = self.turns[self.current_turn]
            for drone_turn in current_turn:
                drone, current_step = drone_turn
                drone_element = self.drones[drone]

                target = self.__get_animation_target(current_step)

                drone_element.move_to(
                    target=pygame.Vector2(target),
                    duration=self.auto_move_delay,
                )

    def reset_turns(self) -> None:
        self.auto_move = False
        self.current_turn = 0
        for drone_element in self.drones.values():
            drone_element.move_to(
                target=pygame.Vector2(
                    self.__get_animation_target(self.map.entry_point)
                ),
                duration=1,
            )
        self.auto_move_delay = 500

    def render(self) -> int:
        clock = pygame.time.Clock()
        running = True
        self.__init_elements()
        combined_dt: int = 0
        dt: int = 0
        last_auto_move_dt: int = 0
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYUP and event.key == pygame.K_q
                ):
                    running = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        self.progress_turn(1)
                    elif event.key == pygame.K_LEFT:
                        self.progress_turn(-1)
                    elif event.key == pygame.K_UP:
                        self.auto_move_delay = max(
                            self.auto_move_delay - 50, 1
                        )
                        for drone_element in self.drones.values():
                            drone_element.animation_duration = (
                                self.auto_move_delay
                            )
                    elif event.key == pygame.K_DOWN:
                        self.auto_move_delay = max(
                            self.auto_move_delay + 50, 1
                        )
                        for drone_element in self.drones.values():
                            drone_element.animation_duration = (
                                self.auto_move_delay
                            )
                    elif event.key == pygame.K_r:
                        self.reset_turns()
                    elif event.key == pygame.K_SPACE:
                        self.auto_move = not self.auto_move
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_manager.cursor_position = pygame.mouse.get_pos()

            _ = self.screen.fill((39, 43, 48))

            self.__draw_elements()

            pygame.display.flip()

            self.__update_elements(dt, combined_dt)

            if (
                self.auto_move
                and combined_dt > 0
                and combined_dt - last_auto_move_dt >= self.auto_move_delay
            ):
                last_auto_move_dt = combined_dt
                self.progress_turn(1)

            dt = clock.tick(self.target_fps)
            combined_dt += dt

        pygame.quit()
        return 0
