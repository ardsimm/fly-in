from typing import Any, Callable, Dict, List, Optional, Tuple


class MouseManager:

    __instance: Optional["MouseManager"] = None

    __mouse_move_subscribers: Dict[
        object,
        Callable[[object, Tuple[int, int]], None]
    ] = {}

    __cursor_position: Tuple[int, int] = (0, 0)

    @classmethod
    def get_instance(cls) -> "MouseManager":
        if cls.__instance is None:
            cls.__instance = MouseManager()
        return cls.__instance

    @property
    def cursor_position(self) -> Tuple[int, int]:
        return self.__cursor_position

    @cursor_position.setter
    def cursor_position(self, pos: Tuple[int, int]) -> None:
        self.__cursor_position = pos
        for subscriber, handler in self.__mouse_move_subscribers.items():
            handler(subscriber, pos)

    def mouse_move_subscribe(
        self,
        subscriber: object,
        handler: Callable[[Any, Tuple[int, int]], None]
    ) -> None:
        self.__mouse_move_subscribers[subscriber] = handler
