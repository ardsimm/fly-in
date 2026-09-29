from math import floor
from typing import Tuple

import pygame
from pygame.math import smoothstep
from typing_extensions import final, override

from src.models.drone import Drone
from src.models.map import Map
from src.visualiser.elements.element import Element
from src.visualiser.managers.coordinate_manager import CoordinateManager
from src.visualiser.managers.font_manager import FontManager


@final
class DroneElement(Element):
    """Drone drawn as a labelled circle, animated between steps."""

    map: Map
    screen: pygame.Surface
    drone: Drone
    max_x: int
    max_y: int
    node_bounding_rect_size: int
    current_turn: int
    __current_pos: pygame.Vector2
    __next_pos: pygame.Vector2
    animation_time: float
    animation_duration: int

    def __init__(
        self,
        map: Map,
        screen: pygame.Surface,
        drone: Drone,
        max_x: int,
        max_y: int,
        node_bounding_rect_size: int,
    ) -> None:
        """Initialise the drone at the start hub.

        Args:
            map: Solved map.
            screen: Surface to draw on.
            drone: Drone to draw.
            max_x: Maximum x coordinate of the map.
            max_y: Maximum y coordinate of the map.
            node_bounding_rect_size: Size of one map unit, in pixels.
        """
        super().__init__()
        self.z_index = 2
        self.screen = screen
        self.drone = drone
        self.max_x = max_x
        self.max_y = max_y
        self.node_bounding_rect_size = node_bounding_rect_size
        self.current_turn = 0
        self.last_move_dt = 0
        self.map = map
        first_step = self.map.entry_point
        self.__current_pos = pygame.Vector2(
            first_step.x,
            first_step.y,
        )
        self.__next_pos = pygame.Vector2(
            first_step.x,
            first_step.y,
        )
        self.animation_time = 0
        self.animation_duration = 500

    @property
    def current_pos(self) -> Tuple[float, float]:
        """Start position of the current animation."""
        return (self.__current_pos.x, self.__current_pos.y)

    @property
    def pos(self) -> pygame.Vector2:
        """Current position, interpolated, in map coordinates."""
        return pygame.Vector2(
            smoothstep(
                self.__current_pos.x, self.__next_pos.x, self.animation_time
            ),
            smoothstep(
                self.__current_pos.y, self.__next_pos.y, self.animation_time
            ),
        )

    @override
    def draw(self) -> None:
        """Draw the drone and its ID."""
        padding_x = 0
        padding_y = 0
        padding_x, padding_y = CoordinateManager.get_paddings(
            self.max_x,
            self.max_y,
            self.node_bounding_rect_size,
            self.screen.height,
            self.screen.width,
        )
        drone_radius = floor(self.node_bounding_rect_size / 6)

        circle_x, circle_y = CoordinateManager.get_node_real_coordinate(
            self.pos.x, self.pos.y, self.node_bounding_rect_size
        )
        circle_x += padding_x
        circle_y += padding_y

        _ = pygame.draw.aacircle(
            self.screen,
            (250, 250, 250),
            pygame.Vector2(circle_x, circle_y),
            drone_radius,
        )

        _ = pygame.draw.aacircle(
            self.screen,
            (50, 50, 50),
            pygame.Vector2(circle_x, circle_y),
            drone_radius - 2,
        )

        font = FontManager.get_font(
            "freesansbold.ttf", floor(drone_radius / 2)
        )

        label_font_render = font.render(
            f"D{self.drone.id}", True, "white", None
        )
        label_rect = label_font_render.get_rect()
        label_rect.center = (circle_x, circle_y)
        _ = self.screen.blit(label_font_render, label_rect)

    def move_to(self, target: pygame.Vector2, duration: int) -> None:
        """Start an animation from the current position.

        Args:
            target: Target position, in map coordinates.
            duration: Duration of the animation, in milliseconds.
        """
        self.__current_pos = self.pos
        self.__next_pos = target
        self.animation_time = 0.0
        self.animation_duration = duration

    @override
    def update(self, dt: int, combined_dt: int) -> None:
        """Advance the animation.

        Args:
            dt: Time since the last frame, in milliseconds.
            combined_dt: Time since the start, in milliseconds.
        """
        self.animation_time += dt / self.animation_duration
