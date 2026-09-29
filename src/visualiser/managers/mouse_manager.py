from typing import Any, Callable, Dict, Optional, Tuple


class MouseManager:
    """Singleton forwarding mouse moves to its subscribers."""

    __instance: Optional["MouseManager"] = None

    __mouse_move_subscribers: Dict[
        object, Callable[[object, Tuple[int, int]], None]
    ] = {}

    __cursor_position: Tuple[int, int] = (0, 0)

    @classmethod
    def get_instance(cls) -> "MouseManager":
        """Get the instance, creating it on first use.

        Returns:
            The MouseManager instance.
        """
        if cls.__instance is None:
            cls.__instance = MouseManager()
        return cls.__instance

    @property
    def cursor_position(self) -> Tuple[int, int]:
        """Last known mouse position, in pixels."""
        return self.__cursor_position

    @cursor_position.setter
    def cursor_position(self, pos: Tuple[int, int]) -> None:
        """Store the mouse position and notify the subscribers.

        Args:
            pos: New mouse position, in pixels.
        """
        self.__cursor_position = pos
        for subscriber, handler in self.__mouse_move_subscribers.items():
            handler(subscriber, pos)

    def mouse_move_subscribe(
        self,
        subscriber: object,
        handler: Callable[[Any, Tuple[int, int]], None],
    ) -> None:
        """Call a handler on every mouse move.

        Args:
            subscriber: Object passed as first argument to the handler.
            handler: Function called with the subscriber and the position.
        """
        self.__mouse_move_subscribers[subscriber] = handler
