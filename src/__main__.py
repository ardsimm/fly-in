import sys
from traceback import print_exception
from typing import List

from src.parser.parser import Parser


class Main:
    @staticmethod
    def main(ac: int, av: List[str]) -> None:
        if ac < 2:
            print("Invalid usage, this program needs a map to run")
            print("Example usage")
            print("uv run python -m src data/maps/easy/01_linear_path.txt")
            print("OR make run MAP=data/maps/easy/01_linear_path.txt")
            sys.exit(1)
        map_path = av[1]
        map_content: str
        try:
            with open(map_path) as file:
                map_content = file.read()
        except OSError as e:
            print(f"Failed to read map file: {e}")
            sys.exit(1)
        parser = Parser()
        print("Parsing map...")
        map = parser.parse(map_content)
        assert map is not None
        print(
            "Great success !"
        )


if __name__ == "__main__":
    try:
        Main.main(len(sys.argv), sys.argv)
    except Exception as e:  # noqa: BLE001
        print("An unhandled exception occured:", file=sys.stderr)
        print_exception(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(0)
