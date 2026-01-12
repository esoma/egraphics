__all__ = ["VkInstance", "use_vulkan", "get_vulkan_instance"]

from contextlib import contextmanager
from typing import Generator
from typing import NewType

from ._egraphics import setup_vulkan
from ._egraphics import shutdown_vulkan

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
        _vulkan_instance = None
        shutdown_vulkan()


def get_vulkan_instance() -> VkInstance:
    if _vulkan_instance is None:
        raise RuntimeError("no vulkan instance is set")
    return _vulkan_instance
