from __future__ import annotations

__all__ = ["GBuffer", "IndexGBuffer", "ReadWriteGBuffer", "VertexGBuffer", "WriteGBuffer"]

from collections.abc import Buffer
from enum import Enum
from itertools import islice
from typing import Any
from typing import ClassVar
from typing import Final
from typing import NamedTuple
from typing import Self
from weakref import ref

from ._egraphics import GL_ARRAY_BUFFER
from ._egraphics import GL_COPY_READ_BUFFER
from ._egraphics import GL_DYNAMIC_COPY
from ._egraphics import GL_DYNAMIC_DRAW
from ._egraphics import GL_DYNAMIC_READ
from ._egraphics import GL_SHADER_STORAGE_BUFFER
from ._egraphics import GL_STATIC_COPY
from ._egraphics import GL_STATIC_DRAW
from ._egraphics import GL_STATIC_READ
from ._egraphics import GL_STREAM_COPY
from ._egraphics import GL_STREAM_DRAW
from ._egraphics import GL_STREAM_READ
from ._egraphics import VK_BUFFER_USAGE_INDEX_BUFFER_BIT
from ._egraphics import VK_BUFFER_USAGE_VERTEX_BUFFER_BIT
from ._egraphics import VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT
from ._egraphics import GlBuffer
from ._egraphics import VkBufferUsageFlags
from ._egraphics import VmaAllocationCreateFlagBits
from ._egraphics import create_vk_buffer
from ._egraphics import create_vk_buffer_memory_view
from ._egraphics import delete_vk_buffer
from ._egraphics import delete_vk_buffer_memory_view
from ._egraphics import flush_vk_buffer
from ._egraphics import invalidate_vk_buffer
from ._egraphics import overwrite_vk_buffer
from ._state import register_reset_state_callback


class GBufferFrequency(Enum):
    STREAM = 0
    STATIC = 1
    DYNAMIC = 2


class GBufferNature(Enum):
    DRAW = 0
    READ = 1
    COPY = 2


_FREQUENCY_NATURE_TO_GL_USAGE: Final = {
    (GBufferFrequency.STREAM, GBufferNature.DRAW): GL_STREAM_DRAW,
    (GBufferFrequency.STREAM, GBufferNature.READ): GL_STREAM_READ,
    (GBufferFrequency.STREAM, GBufferNature.COPY): GL_STREAM_COPY,
    (GBufferFrequency.STATIC, GBufferNature.DRAW): GL_STATIC_DRAW,
    (GBufferFrequency.STATIC, GBufferNature.READ): GL_STATIC_READ,
    (GBufferFrequency.STATIC, GBufferNature.COPY): GL_STATIC_COPY,
    (GBufferFrequency.DYNAMIC, GBufferNature.DRAW): GL_DYNAMIC_DRAW,
    (GBufferFrequency.DYNAMIC, GBufferNature.READ): GL_DYNAMIC_READ,
    (GBufferFrequency.DYNAMIC, GBufferNature.COPY): GL_DYNAMIC_COPY,
}


class GBufferTarget:
    _targets: ClassVar[list[GBufferTarget]] = []

    ARRAY: ClassVar[Self]
    COPY_READ: ClassVar[Self]
    SHADER_STORAGE: ClassVar[Self]

    def __init__(self, gl_target: Any):
        self._targets.append(self)
        self._gl_target = gl_target
        self._g_buffer: ref[GBuffer] | None = None

    @property
    def g_buffer(self) -> GBuffer | None:
        if self._g_buffer is not None:
            return self._g_buffer()
        return None

    @g_buffer.setter
    def g_buffer(self, g_buffer: GBuffer | None) -> None:
        return


GBufferTarget.ARRAY = GBufferTarget(GL_ARRAY_BUFFER)
GBufferTarget.COPY_READ = GBufferTarget(GL_COPY_READ_BUFFER)
GBufferTarget.SHADER_STORAGE = GBufferTarget(GL_SHADER_STORAGE_BUFFER)


@register_reset_state_callback
def _reset_g_buffer_target_state() -> None:
    pass


class GBuffer:
    _buffer: memoryview | None = None
    _buffer_refs: int = 0
    __usage: ClassVar[VkBufferUsageFlags] = 0  # type: ignore
    __vma_flags: ClassVar[VmaAllocationCreateFlagBits] = 0  # type: ignore

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        for c in cls.__mro__:
            cls.__usage |= getattr(c, "_egraphics__g_buffer_usage", 0)  # type: ignore
            cls.__vma_flags |= getattr(c, "_egraphics__g_buffer_vma_flags", 0)  # type: ignore

    def __init__(self, length: int):
        if self.__usage == 0:
            raise RuntimeError(f"{self.__class__.__name__} cannot be instantiated")
        self._vk_buffer, self._vma_allocation = create_vk_buffer(
            length, self.__usage, self.__vma_flags
        )
        self._length = length

    def __del__(self) -> None:
        if not hasattr(self, "_vk_buffer"):
            return
        delete_vk_buffer(self._vk_buffer, self._vma_allocation)
        del self._vk_buffer

    def __len__(self) -> int:
        return self._length


class IndexGBuffer(GBuffer):
    _egraphics__g_buffer_usage: ClassVar = VK_BUFFER_USAGE_INDEX_BUFFER_BIT


class VertexGBuffer(GBuffer):
    _egraphics__g_buffer_usage: ClassVar = VK_BUFFER_USAGE_VERTEX_BUFFER_BIT


class WriteGBuffer(GBuffer):
    _egraphics__g_buffer_vma_flags: ClassVar = (
        VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT
    )

    def __init__(self, data: Buffer | int):
        if isinstance(data, int):
            length = data
        else:
            length = len(memoryview(data))
        super().__init__(length)
        if not isinstance(data, int):
            overwrite_vk_buffer(self._vk_buffer, self._vma_allocation, 0, data)

    def write(self, data: Buffer, *, offset: int = 0) -> None:
        data_length = len(memoryview(data))
        if data_length == 0:
            return
        if offset < 0:
            raise ValueError("underflow")
        if offset + data_length > len(self):
            raise ValueError("overflow")
        overwrite_vk_buffer(self._vk_buffer, self._vma_allocation, offset, data)


class ReadWriteGBuffer(WriteGBuffer):
    _egraphics__g_buffer_vma_flags: ClassVar = (
        VMA_ALLOCATION_CREATE_HOST_ACCESS_SEQUENTIAL_WRITE_BIT
    )
    _buffer: memoryview | None = None
    _buffer_refs: int = 0

    def __buffer__(self, flags: int) -> memoryview:
        if self._buffer_refs:
            assert self._buffer is not None
            self._buffer_refs += 1
            return self._buffer

        assert self._buffer is None
        assert self._buffer_refs == 0

        self._buffer = create_vk_buffer_memory_view(
            self._vk_buffer, self._vma_allocation, self._length
        )
        self._buffer_refs += 1
        return self._buffer

    def __release_buffer__(self, view: memoryview) -> None:
        self._buffer_refs -= 1
        assert self._buffer_refs >= 0
        if self._buffer_refs != 0:
            return

        self._buffer = None
        delete_vk_buffer_memory_view(self._vk_buffer, self._vma_allocation)

    def flush(self) -> None:
        flush_vk_buffer(self._vk_buffer, self._vma_allocation)

    def clear_cache(self) -> None:
        invalidate_vk_buffer(self._vk_buffer, self._vma_allocation)


def get_g_buffer_gl_buffer(g_buffer: GBuffer) -> GlBuffer:
    return GlBuffer(0)


class _WriteGBuffer(NamedTuple):
    data: Buffer
    offset: int


class EditGBuffer:
    def __init__(self, g_buffer: WriteGBuffer):
        self._g_buffer = g_buffer
        self._write_buffer: list[_WriteGBuffer] = []

    def write(self, data: Buffer, *, offset: int = 0) -> None:
        self._write_buffer.append(_WriteGBuffer(data, offset))

    def flush(self) -> None:
        if not self._write_buffer:
            return

        self._write_buffer.sort(key=lambda w: w.offset)
        data = bytearray(self._write_buffer[0].data)
        offset = self._write_buffer[0].offset
        for write in islice(self._write_buffer, 1, None):
            if write.offset == offset + len(data):
                data += write.data
            else:
                overwrite_vk_buffer(
                    self._g_buffer._vk_buffer, self._g_buffer._vma_allocation, offset, data
                )
                data = bytearray(write.data)
                offset = write.offset
        overwrite_vk_buffer(
            self._g_buffer._vk_buffer, self._g_buffer._vma_allocation, offset, data
        )
        self._write_buffer.clear()

    def clear(self) -> None:
        self._write_buffer.clear()

    @property
    def g_buffer(self) -> WriteGBuffer:
        return self._g_buffer
