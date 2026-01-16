__all__ = ["GCommandPool"]

from typing import ClassVar
from typing import Collection
from typing import Generic
from typing import TypeVar

from ._g_command import GCommand
from ._g_command_queue import GCommandQueue
from ._g_command_queue import get_g_command_queue_vk
from ._lifetime import LifetimeChild
from ._lifetime import LifetimeParent

_C = TypeVar("_C", bound=GCommand)


class GCommandPool(LifetimeParent, LifetimeChild, Generic[_C]):
    _GCommandPool__supports_individual_command_reset: ClassVar[bool] = False
    _GCommandPool__vk: VkCommandPool | None = None

    def __init__(self, queue: GCommandQueue[_C], *, is_transient: bool = False):
        super().__init__(lifetime_parent=queue)
        queue_vk = get_g_command_queue_vk(queue)

        flags: VkCommandPoolCreateFlagBits = 0
        if is_transient:
            flags |= VK_COMMAND_POOL_CREATE_TRANSIENT_BIT
        if self._GCommandPool__supports_individual_command_reset:
            flags |= VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT
        self._GCommandPool__vk = create_vk_command_pool(queue_vk.family_index)

    def close(self) -> None:
        super().close()
        if self._GCommandPool__vk is not None:
            delete_vk_command_pool(self._GCommandPool__vk)
            self._GCommandPool__vk = None

    def reset(self) -> None:
        pass


class IndividualResetGCommandPool(GCommandPool[_C]):
    _GCommandPool__supports_individual_command_reset: ClassVar[bool] = True

    def reset(self, *, commands: Collection[_C] = ()) -> None:
        pass
