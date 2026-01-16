__all__ = ["Lifetime", "LifetimeParent", "LifetimeChild"]

from typing import Any
from typing import Self
from weakref import WeakSet


class Lifetime:
    __is_open: bool = True

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        self.__is_open = False

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self.close()

    @property
    def is_open(self):
        return self.__is_open


class LifetimeParent(Lifetime):
    def __init__(self, *args: Any, **kwargs: Any):
        self._LifetimeParent__children: WeakSet[Lifetime] = WeakSet()
        super().__init__(*args, **kwargs)

    def close(self) -> None:
        while True:
            try:
                child = self._LifetimeParent__children.pop()
            except (KeyError, AttributeError):
                break
            child.close()
        super().close()


class LifetimeChild(Lifetime):
    def __init__(self, *args: Any, lifetime_parent: LifetimeParent, **kwargs: Any):
        self.__lifetime_parent = lifetime_parent
        lifetime_parent._LifetimeParent__children.add(self)
        super().__init__(*args, **kwargs)

    def close(self) -> None:
        try:
            self.__lifetime_parent._LifetimeParent__children.remove(self)
        except KeyError:
            pass
        super().close()
