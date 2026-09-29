import json
import sys
from typing import Dict, Optional, Union

import pygame

BORING_BACKUP_DICT = {
    "red": "red",
    "blue": "blue",
    "black": "black",
    "yellow": "yellow",
    "pink": "pink",
    "violet": "violet",
    "mauve": "mauve",
    "orange": "orange",
    "brown": "brown",
    "teal": "teal",
    "magenta": "magenta",
}


class ColorManager:

    __colors_dict: Optional[Dict[str, str]] = None

    @classmethod
    def get_colors_dict(cls) -> Dict[str, str]:
        if cls.__colors_dict is None:
            try:
                with open("data/colors.json") as colors_files:
                    cls.__colors_dict = json.loads(colors_files.read())
            except (OSError, json.JSONDecodeError):
                print(
                    "ERROR: Failed to load colors file,",
                    "using boring backup dict",
                    file=sys.stderr,
                )
                cls.__colors_dict = BORING_BACKUP_DICT
        assert cls.__colors_dict is not None
        return cls.__colors_dict

    @classmethod
    def get_color(cls, color_name: str) -> pygame.Color:
        color_value = cls.get_colors_dict().get(color_name)
        if not color_value:
            try:
                return pygame.Color(color_name)
            except ValueError:
                color_value = "black"
        return pygame.Color(color_value)
