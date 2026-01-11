__all__ = ["VkInstance", "use_vulkan_instance", "get_vulkan_instance"]

from contextlib import contextmanager
from typing import Generator
from typing import NewType

VkInstance = NewType("VkInstance", int)

_vulkan_instance: VkInstance | None = None


@contextmanager
def use_vulkan_instance(instance: VkInstance) -> Generator[None, None, None]:
    global _vulkan_instance
    if _vulkan_instance is not None:
        raise RuntimeError("a vulkan instance is already set")
    _vulkan_instance = instance
    yield
    _vulkan_instance = None


def get_vulkan_instance() -> VkInstance:
    if _vulkan_instance is None:
        raise RuntimeError("no vulkan instance is set")
    return _vulkan_instance
