import json
import os
import sys
from typing import Dict, Optional

import pygame

BORING_BACKUP_DICT = {
    "red": "red",
    "blue": "blue",
    "black": "black",
    "yellow": "yellow",
    "pink": "pink",
    "violet": "violet",
    "orange": "orange",
    "brown": "brown",
    "teal": "teal",
    "magenta": "magenta",
}


class ColorManager:
    """Resolve free-form color names to pygame colors."""

    __colors_dict: Optional[Dict[str, str]] = None

    @classmethod
    def get_colors_dict(cls) -> Dict[str, str]:
        """Load data/colors.json once, or fall back to a built-in dict.

        Returns:
            The hex value of each known color name.
        """
        if cls.__colors_dict is None:
            try:
                with open(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "..",
                        "..",
                        "data",
                        "colors.json",
                    )
                ) as colors_files:
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
        """Resolve a color name.

        Args:
            color_name: Color name from the map.

        Returns:
            The color from colors.json, else pygame's color of that name,
            else black.
        """
        color_value = cls.get_colors_dict().get(color_name)
        if not color_value:
            try:
                return pygame.Color(color_name)
            except ValueError:
                color_value = "black"
        return pygame.Color(color_value)
