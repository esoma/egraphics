from ._g_command import GCommand
from ._g_command_queue import GCommandQueue


class GCommandPool:
    def __init__(self, queue: GCommandQueue):
        pass

    def acquire(self) -> GCommand:
        pass

    def release(self, command: GCommand) -> None:
        pass


class ResetGCommandPool(GCommandPool):
    def reset(self) -> None:
        pass
