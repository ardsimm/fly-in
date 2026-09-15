import sys
from typing import Tuple
import pygame
from src.visualiser.color_palette import ColorPaletteTypedDict


class Visualiser:

    colors: ColorPaletteTypedDict
    dimensions: Tuple[int, int]
    target_fps: int

    def __init__(
        self,
        color_palette: ColorPaletteTypedDict = {},
        dimensions: Tuple[int, int] = (800, 800),
        target_fps: int = 60
    ) -> None:
        self.colors = color_palette
        self.dimensions = dimensions
        self.target_fps = target_fps

    def render(self) -> int:
        pygame.init()
        screen = pygame.display.set_mode(self.dimensions)
        clock = pygame.time.Clock()
        running = True
        dt = 0

        player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

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

                # fill the screen with a color to wipe away anything from last frame
                screen.fill("white")

                pygame.draw.circle(screen, "red", player_pos, 40)
                pygame.display.flip()

                # limits FPS to 60
                clock.tick(self.target_fps)
        except BaseException as e:
            print(f"An unhandled excetion occured:\n{e}", file=sys.stderr)
            pygame.quit()
            return 1

        pygame.quit()
        return 0
