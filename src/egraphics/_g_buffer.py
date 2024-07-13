from __future__ import annotations

__all__ = [
    "get_g_buffer_gl_buffer",
    "GBuffer",
    "GBufferTarget",
    "GBufferFrequency",
    "GBufferNature",
]

# egraphics
from ._egraphics import GL_ARRAY_BUFFER
from ._egraphics import GL_COPY_READ_BUFFER
from ._egraphics import GL_DYNAMIC_COPY
from ._egraphics import GL_DYNAMIC_DRAW
from ._egraphics import GL_DYNAMIC_READ
from ._egraphics import GL_ELEMENT_ARRAY_BUFFER
from ._egraphics import GL_STATIC_COPY
from ._egraphics import GL_STATIC_DRAW
from ._egraphics import GL_STATIC_READ
from ._egraphics import GL_STREAM_COPY
from ._egraphics import GL_STREAM_DRAW
from ._egraphics import GL_STREAM_READ
from ._egraphics import create_gl_buffer
from ._egraphics import create_gl_copy_read_buffer_memory_view
from ._egraphics import delete_gl_buffer
from ._egraphics import release_gl_copy_read_buffer_memory_view
from ._egraphics import set_gl_buffer_target
from ._egraphics import set_gl_buffer_target_data

# eplatform
from eplatform import Platform

# python
from collections.abc import Buffer
from enum import Enum
from typing import Any
from typing import ClassVar
from typing import Final
from typing import Self
from typing import TypeAlias
from weakref import ref


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
    ELEMENT_ARRAY: ClassVar[Self]

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
        if self.g_buffer is g_buffer:
            return
        if g_buffer is None:
            set_gl_buffer_target(self._gl_target, None)
            self._g_buffer = None
        else:
            set_gl_buffer_target(self._gl_target, g_buffer._gl_buffer)
            self._g_buffer = ref(g_buffer)


GBufferTarget.ARRAY = GBufferTarget(GL_ARRAY_BUFFER)
GBufferTarget.COPY_READ = GBufferTarget(GL_COPY_READ_BUFFER)
GBufferTarget.ELEMENT_ARRAY = GBufferTarget(GL_ELEMENT_ARRAY_BUFFER)


@Platform.register_deactivate_callback
def _reset_g_buffer_target_state() -> None:
    for target in GBufferTarget._targets:
        target.g_buffer = None


class GBuffer:
    _buffer: memoryview | None = None
    _buffer_refs: int = 0

    Nature: TypeAlias = GBufferNature
    Frequency: TypeAlias = GBufferFrequency
    Target: TypeAlias = GBufferTarget

    def __init__(
        self,
        data: Buffer | int = 0,
        *,
        frequency: GBufferFrequency = GBufferFrequency.STATIC,
        nature: GBufferNature = GBufferNature.DRAW,
    ):
        self._gl_usage = _FREQUENCY_NATURE_TO_GL_USAGE[(frequency, nature)]
        self._frequency = frequency
        self._nature = nature

        self._gl_buffer = create_gl_buffer()
        GBufferTarget.ARRAY.g_buffer = self
        self._length = set_gl_buffer_target_data(GL_ARRAY_BUFFER, data, self._gl_usage)

    def __del__(self) -> None:
        if not hasattr(self, "_gl_buffer"):
            return
        delete_gl_buffer(self._gl_buffer)
        del self._gl_buffer

    def __len__(self) -> int:
        return self._length

    def __buffer__(self, flags: int) -> memoryview:
        if self._buffer_refs:
            assert self._buffer is not None
            self._buffer_refs += 1
            return self._buffer

        assert self._buffer is None
        assert self._buffer_refs == 0

        if self._length == 0:
            self._buffer = memoryview(b"").cast("B")
            self._buffer_refs += 1
            return self._buffer

        GBufferTarget.COPY_READ.g_buffer = self
        self._buffer = create_gl_copy_read_buffer_memory_view(self._length)
        self._buffer_refs += 1
        return self._buffer

    def __release_buffer__(self, view: memoryview) -> None:
        self._buffer_refs -= 1
        assert self._buffer_refs >= 0
        if self._buffer_refs != 0:
            return

        if self._length != 0:
            GBufferTarget.COPY_READ.g_buffer = self
            release_gl_copy_read_buffer_memory_view()

        self._buffer = None

    @property
    def frequency(self) -> GBufferFrequency:
        return self._frequency

    @property
    def nature(self) -> GBufferNature:
        return self._nature
