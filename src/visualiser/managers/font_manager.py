from typing import Dict, Tuple

import pygame
from pygame.typing import FileLike


class FontManager:

    fonts: Dict[Tuple[FileLike, int], pygame.Font] = {}

    @classmethod
    def get_font(cls, name: FileLike, size: int) -> pygame.Font:
        return cls.fonts.setdefault((name, size), pygame.font.Font(
            name, size
        ))
