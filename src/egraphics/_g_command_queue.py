__all__ = ["GCommandQueue"]


from typing import Generic
from typing import TypeVar

from ._egraphics import VkQueue
from ._egraphics import acquire_vk_queue
from ._egraphics import release_vk_queue
from ._g_command import GCommand
from ._g_command import get_g_command_requirements
from ._vulkan import VulkanObject

_C = TypeVar("_C", bound=GCommand)


class GCommandQueue(VulkanObject, Generic[_C]):
    _GCommandQueue__vk: VkQueue | None = None

    def __init__(self, command: type[_C]):
        self.__command = command
        requirements = get_g_command_requirements(command)
        self._GCommandQueue__vk = acquire_vk_queue(
            requirements.graphics,
            requirements.compute,
            requirements.transfer,
            requirements.presentation,
        )
        super().__init__()

    def close(self) -> None:
        if self._GCommandQueue__vk is not None:
            release_vk_queue(self._GCommandQueue__vk)
            self._GCommandQueue__vk = None
        super().close()

    @property
    def command(self) -> type[_C]:
        return self.__command
