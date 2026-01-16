__all__ = [
    "GCommandQueue",
    "ComputeGCommandQueue",
    "GeneralGCommandQueue",
    "GraphicsGCommandQueue",
    "PresentationGCommandQueue",
    "TransferGCommandQueue",
]

from typing import Any
from typing import ClassVar

from ._egraphics import VkQueue
from ._egraphics import acquire_vk_queue
from ._egraphics import release_vk_queue
from ._vulkan import VulkanObject


class GCommandQueue(VulkanObject):
    __supports_transfer: ClassVar[bool] = False
    __supports_compute: ClassVar[bool] = False
    __supports_graphics: ClassVar[bool] = False
    __supports_presentation: ClassVar[bool] = False

    _GCommandQueue__vk: VkQueue | None = None

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        for c in cls.__mro__:
            if getattr(c, "_egraphics_GCommandQueue__supports_transfer", False):
                cls.__supports_transfer = True
            if getattr(c, "_egraphics_GCommandQueue__supports_compute", False):
                cls.__supports_compute = True
            if getattr(c, "_egraphics_GCommandQueue__supports_graphics", False):
                cls.__supports_graphics = True
            if getattr(c, "_egraphics_GCommandQueue__supports_presentation", False):
                cls.__supports_presentation = True

    def __init__(self):
        self._GCommandQueue__vk = acquire_vk_queue(
            self.__supports_graphics,
            self.__supports_compute,
            self.__supports_transfer,
            self.__supports_presentation,
        )
        super().__init__()

    def close(self) -> None:
        if self._GCommandQueue__vk is not None:
            release_vk_queue(self._GCommandQueue__vk)
            self._GCommandQueue__vk = None
        super().close()


class TransferGCommandQueue(GCommandQueue):
    _egraphics_GCommandQueue__supports_transfer: ClassVar = True


class ComputeGCommandQueue(TransferGCommandQueue):
    _egraphics_GCommandQueue__supports_compute: ClassVar = True


class GraphicsGCommandQueue(TransferGCommandQueue):
    _egraphics_GCommandQueue__supports_graphics: ClassVar = True


class PresentationGCommandQueue(GCommandQueue):
    _egraphics_GCommandQueue__supports_presentation: ClassVar = True


class GeneralGCommandQueue(ComputeGCommandQueue, GraphicsGCommandQueue, PresentationGCommandQueue):
    pass
