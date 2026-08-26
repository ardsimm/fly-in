import sys
from traceback import print_exception


class Main:

    @staticmethod
    def main() -> None:
        print("Hello World !")


if __name__ == "__main__":
    try:
        Main.main()
    except Exception as e:
        print("An unhandled exception occured:", file=sys.stderr)
        print_exception(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(0)
