from collections.abc import Callable
from typing import ParamSpec, List, Generic

P = ParamSpec('P')


class Observable(Generic[P]):
    def __init__(self):
        self.callbacks: List[Callable[P, None]] = []

    def on(self, callback: Callable[P, None]):
        self.callbacks.append(callback)

    def off(self, callback: Callable[P, None]):
        self.callbacks.remove(callback)

    def fire(self, *args: P.args, **kwargs: P.kwargs) -> None:
        for callback in self.callbacks:
            callback(*args, **kwargs)
