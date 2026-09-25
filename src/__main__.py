import sys
from traceback import print_exception

from src.parser import Parser, ParsingError
from src.simulation import PathNotFoundError, Simulation
from src.visualiser import Visualiser


class Main:
    @staticmethod
    def main(ac: int, av: list[str]) -> int:
        if ac < 2:
            print("Invalid usage, this program needs a map to run")
            print("Example usage")
            print("uv run python -m src data/maps/easy/01_linear_path.txt")
            print("OR make run MAP=data/maps/easy/01_linear_path.txt")
            return 1
        map_path = av[1]
        map_content: str
        try:
            with open(map_path) as file:
                map_content = file.read()
        except OSError as e:
            print(f"Failed to read map file: {e}")
            return 1
        parser = Parser()
        print("Parsing map...")
        try:
            map = parser.parse(map_content)
        except ParsingError as e:
            print(e, file=sys.stderr)
            return 1
        assert map is not None
        print("Successfuly parsed map, checking if it is solvable...")
        simulation = Simulation()
        try:
            simulation.check_solvable(map)
        except PathNotFoundError:
            print("Error: map is not solvable", file=sys.stderr)
            return 1
        print("Map is solvable ! solving map...")
        print("Solution:")
        turns = simulation.get_turns(map, simulation.cooperative_bfs(map))
        i = 0
        for i, turn in enumerate(turns):
            print(f"========== step {i + 1} ===========")
            for step in turn:
                print(f"D{step[0].id}:{step[1].name} ({step[2]} drones)")
        print("=============================")
        print("Solution found in", i + 1, "turn" + ("s." if i > 0 else "."))
        return Visualiser(map).render()
        return 0


if __name__ == "__main__":
    try:
        sys.exit(Main.main(len(sys.argv), sys.argv))
    except Exception as e:  # noqa: BLE001
        print("An unhandled exception occured:", file=sys.stderr)
        print_exception(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(0)
