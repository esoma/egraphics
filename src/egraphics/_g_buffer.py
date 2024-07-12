from __future__ import annotations

__all__ = [
    "GBuffer",
    "GBufferTarget",
    "GBufferFrequency",
    "GBufferNature",
]


# eplatform
from eplatform import Platform

# pyopengl
from OpenGL.GL import GL_ARRAY_BUFFER
from OpenGL.GL import GL_COPY_READ_BUFFER
from OpenGL.GL import GL_DYNAMIC_COPY
from OpenGL.GL import GL_DYNAMIC_DRAW
from OpenGL.GL import GL_DYNAMIC_READ
from OpenGL.GL import GL_READ_WRITE
from OpenGL.GL import GL_STATIC_COPY
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import GL_STATIC_READ
from OpenGL.GL import GL_STREAM_COPY
from OpenGL.GL import GL_STREAM_DRAW
from OpenGL.GL import GL_STREAM_READ
from OpenGL.GL import glBindBuffer
from OpenGL.GL import glBufferData
from OpenGL.GL import glDeleteBuffers
from OpenGL.GL import glGenBuffers
from OpenGL.GL import glMapBuffer
from OpenGL.GL import glUnmapBuffer
from OpenGL.error import GLError
from OpenGL.error import NullFunctionError

# python
from collections.abc import Buffer
from ctypes import POINTER as c_pointer
from ctypes import c_ubyte
from ctypes import c_void_p
from ctypes import cast as c_cast
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
            glBindBuffer(self._gl_target, 0)
            self._g_buffer = None
        else:
            glBindBuffer(self._gl_target, g_buffer._gl_buffer)
            self._g_buffer = ref(g_buffer)


GBufferTarget.ARRAY = GBufferTarget(GL_ARRAY_BUFFER)
GBufferTarget.COPY_READ = GBufferTarget(GL_COPY_READ_BUFFER)


@Platform.register_deactivate_callback
def _reset_g_buffer_target_state() -> None:
    for target in GBufferTarget._targets:
        target.g_buffer = None


class GBuffer:
    _buffer: Any = None
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
        if isinstance(data, int):
            if data < 0:
                raise ValueError("data must be 0 or more")
            self._length = data
            buffer = None
        else:
            buffer = memoryview(data)
            self._length = buffer.nbytes

        self._gl_usage = _FREQUENCY_NATURE_TO_GL_USAGE[(frequency, nature)]
        self._frequency = frequency
        self._nature = nature

        self._gl_buffer: int = glGenBuffers(1)
        GBufferTarget.ARRAY.g_buffer = self
        glBufferData(GL_ARRAY_BUFFER, self._length, buffer, self._gl_usage)

    def __del__(self) -> None:
        if not hasattr(self, "_gl_buffer"):
            return
        try:
            try:
                glDeleteBuffers(1, [self._gl_buffer])
            except (TypeError, NullFunctionError, GLError):
                pass
            del self._gl_buffer
        except AttributeError:
            pass

    def __len__(self) -> int:
        return self._length

    def __buffer__(self, flags: int) -> memoryview:
        if self._buffer:
            self._buffer_refs += 1
            return self._create_memory_view()

        if self._length == 0:
            self._buffer = b""
        else:
            GBufferTarget.COPY_READ.g_buffer = self
            map = c_void_p(glMapBuffer(GL_COPY_READ_BUFFER, GL_READ_WRITE))
            self._buffer = c_cast(map, c_pointer(c_ubyte * self._length)).contents
        self._buffer_refs = 1
        return self._create_memory_view()

    def __release_buffer__(self, view: memoryview) -> None:
        self._buffer_refs -= 1
        assert self._buffer_refs >= 0
        if self._buffer_refs != 0:
            return

        if not isinstance(self._buffer, bytes):
            GBufferTarget.COPY_READ.g_buffer = self
            glUnmapBuffer(GL_COPY_READ_BUFFER)

        self._buffer = None

    def _create_memory_view(self) -> memoryview:
        assert self._buffer is not None
        return memoryview(self._buffer).cast("B")

    @property
    def frequency(self) -> GBufferFrequency:
        return self._frequency

    @property
    def gl_buffer(self) -> int:
        return self._gl_buffer

    @property
    def nature(self) -> GBufferNature:
        return self._nature
