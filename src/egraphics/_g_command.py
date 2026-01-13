__all__ = ["GCommandQueue", "GraphicsGCommandQueue", "PresentationGCommandQueue"]


class GCommandQueue:
    __supports_graphics: ClassVar[bool] = False
    __supports_presentation: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        for c in cls.__mro__:
            if getattr(c, "_egraphics__g_command_queue_supports_graphics", False):
                cls.__supports_graphics = True
            if getattr(c, "_egraphics__g_command_queue_supports_presentation", False):
                cls.__supports_presentation = True

    def __init__(self):
        self._vk_queue = acquire_vk_queue(self.__supports_graphics, self.__supports_presentation)

    def __del__(self) -> None:
        if not hasattr(self, "_vk_buffer"):
            return
        release_vk_queue(self._vk_queue)
        del self._vk_buffer


class GraphicsGCommandQueue(GCommandQueue):
    _egraphics__g_command_queue_supports_graphics: ClassVar = True


class PresentationGCommandQueue(GCommandQueue):
    _egraphics__g_command_queue_supports_presentation: ClassVar = True
