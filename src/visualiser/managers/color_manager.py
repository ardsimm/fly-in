from math import floor
from typing import Tuple

from matplotlib import colors


class ColorManager:

    @staticmethod
    def get_color_in_rgb(color: str) -> Tuple[int, int, int]:
        try:
            r, g, b = colors.to_rgb(color)
        except ValueError:
            print(f"Waning: unknown color {color}, defaulting to black.")
            color = "red"
            r, g, b = colors.to_rgb(color)
        return (floor(r * 255), floor(g * 255), floor(b * 255))
