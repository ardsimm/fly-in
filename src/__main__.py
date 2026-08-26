from sys import stderr
from traceback import print_exception


class Main:

    @staticmethod
    def main() -> None:
        print("Hello World !")


if __name__ == "__main__":
    try:
        Main.main()
    except Exception as e:
        print("An unhandled exception occured:", file=stderr)
        print_exception(e)
