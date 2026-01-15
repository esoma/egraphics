__all__ = ["VkInstance", "use_vulkan", "VulkanObject"]

from contextlib import contextmanager
from typing import Any
from typing import Generator
from typing import NewType
from typing import Self
from weakref import WeakSet

from ._egraphics import setup_vulkan
from ._egraphics import shutdown_vulkan


class VulkanObject:
    __is_open: bool = True

    def __init__(self) -> None:
        assert _vulkan_instance is not None
        _open_objects.add(self)

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        try:
            _open_objects.remove(self)
        except KeyError:
            pass
        self.__is_open = False

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self.close()

    @property
    def is_open(self):
        return self.__is_open


_open_objects: WeakSet[VulkanObject] = WeakSet()

VkInstance = NewType("VkInstance", int)

_vulkan_instance: VkInstance | None = None


@contextmanager
def use_vulkan(instance: int, surface: int) -> Generator[None, None, None]:
    global _vulkan_instance
    if _vulkan_instance is not None:
        raise RuntimeError("a vulkan instance is already set")
    setup_vulkan(instance, surface)
    _vulkan_instance = VkInstance(instance)
    try:
        yield
    finally:
        while True:
            try:
                open_object = _open_objects.pop()
            except KeyError:
                break
            open_object.close()
        _vulkan_instance = None
        shutdown_vulkan()
