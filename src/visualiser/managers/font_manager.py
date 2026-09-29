from typing import Dict, Tuple

import pygame
from pygame.typing import FileLike


class FontManager:

    fonts: Dict[Tuple[FileLike, int], pygame.Font] = {}

    @classmethod
    def get_font(cls, name: FileLike, size: int) -> pygame.Font:
        font = cls.fonts.get((name, size))
        if font is None:
            cls.fonts[(name, size)] = pygame.font.Font(
                name, size
            )
        assert cls.fonts[(name, size)] is not None
        return cls.fonts[(name, size)]
