from __future__ import annotations

__all__ = [
    "EditGBuffer",
    "GBuffer",
    "GBufferTarget",
    "GBufferFrequency",
    "GBufferNature",
    "bind_g_buffer_shader_storage_buffer_unit",
    "get_g_buffer_gl_buffer",
]

from collections.abc import Buffer
from enum import Enum
from itertools import islice
from typing import Any
from typing import ClassVar
from typing import Final
from typing import NamedTuple
from typing import Self
from typing import TypeAlias
from weakref import ref

from ._egraphics import GL_ARRAY_BUFFER
from ._egraphics import GL_COPY_READ_BUFFER
from ._egraphics import GL_DYNAMIC_COPY
from ._egraphics import GL_DYNAMIC_DRAW
from ._egraphics import GL_DYNAMIC_READ
from ._egraphics import GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS_VALUE
from ._egraphics import GL_SHADER_STORAGE_BUFFER
from ._egraphics import GL_STATIC_COPY
from ._egraphics import GL_STATIC_DRAW
from ._egraphics import GL_STATIC_READ
from ._egraphics import GL_STREAM_COPY
from ._egraphics import GL_STREAM_DRAW
from ._egraphics import GL_STREAM_READ
from ._egraphics import GlBuffer
from ._egraphics import create_gl_buffer
from ._egraphics import create_gl_buffer_memory_view
from ._egraphics import delete_gl_buffer
from ._egraphics import release_gl_buffer_memory_view
from ._egraphics import set_gl_buffer_target
from ._egraphics import set_gl_buffer_target_data
from ._egraphics import set_shader_storage_buffer_unit
from ._egraphics import write_gl_buffer_target_data
from ._state import register_reset_state_callback
from ._weak_fifo_set import WeakFifoSet


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
GBufferTarget.SHADER_STORAGE = GBufferTarget(GL_SHADER_STORAGE_BUFFER)


@register_reset_state_callback
def _reset_g_buffer_target_state() -> None:
    for target in GBufferTarget._targets:
        target._g_buffer = None
    GBuffer._max_shader_storage_buffer_unit = None
    GBuffer._next_shader_storage_buffer_unit = 0
    GBuffer._unbound_shader_storage_buffer_units.clear()


class GBuffer:
    _buffer: memoryview | None = None
    _buffer_refs: int = 0

    _max_shader_storage_buffer_unit: ClassVar[int | None] = None
    _next_shader_storage_buffer_unit: ClassVar[int] = 0
    _unbound_shader_storage_buffer_units: ClassVar[WeakFifoSet[GBuffer]] = WeakFifoSet()
    _shader_storage_buffer_unit: int | None = None
    _open_shader_storage_buffer_units: set[int] = set()

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
        self._buffer = create_gl_buffer_memory_view(GL_COPY_READ_BUFFER, self._length)
        self._buffer_refs += 1
        return self._buffer

    def __release_buffer__(self, view: memoryview) -> None:
        self._buffer_refs -= 1
        assert self._buffer_refs >= 0
        if self._buffer_refs != 0:
            return

        if self._length != 0:
            GBufferTarget.COPY_READ.g_buffer = self
            release_gl_buffer_memory_view(GL_COPY_READ_BUFFER)

        self._buffer = None

    def write(self, data: Buffer, *, offset: int = 0) -> None:
        GBufferTarget.ARRAY.g_buffer = self
        write_gl_buffer_target_data(GL_ARRAY_BUFFER, data, offset)

    @property
    def frequency(self) -> GBufferFrequency:
        return self._frequency

    @property
    def nature(self) -> GBufferNature:
        return self._nature

    def _acquire_shader_storage_buffer_unit(self) -> None:
        if self._open_shader_storage_buffer_units:
            self._shader_storage_buffer_unit = self._open_shader_storage_buffer_units.pop()
            return
        assert self._next_shader_storage_buffer_unit <= GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS_VALUE
        if self._next_shader_storage_buffer_unit == GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS_VALUE:
            self._steal_shader_storage_buffer_unit()
        else:
            self._shader_storage_buffer_unit = self._next_shader_storage_buffer_unit
            GBuffer._next_shader_storage_buffer_unit += 1

    def _release_shader_storage_buffer_unit(self) -> None:
        assert self._shader_storage_buffer_unit is not None
        self._open_shader_storage_buffer_units.add(self._shader_storage_buffer_unit)
        self._shader_storage_buffer_unit = None
        try:
            self._unbound_shader_storage_buffer_units.remove(self)
        except KeyError:
            pass

    def _steal_shader_storage_buffer_unit(self) -> None:
        try:
            g_buffer = self._unbound_shader_storage_buffer_units.pop()
        except IndexError:
            raise RuntimeError("no shader storage buffer unit available")
        g_buffer._release_shader_storage_buffer_unit()
        self._acquire_shader_storage_buffer_unit()

    def _bind_shader_storage_buffer_unit(self) -> None:
        if self._shader_storage_buffer_unit is None:
            self._acquire_shader_storage_buffer_unit()
        assert self._shader_storage_buffer_unit is not None
        assert self._gl_buffer is not None
        set_shader_storage_buffer_unit(self._shader_storage_buffer_unit, self._gl_buffer)

    def _unbind_shader_storage_buffer_unit(self) -> None:
        assert self._shader_storage_buffer_unit is not None
        self._unbound_shader_storage_buffer_units.add(self)


def get_g_buffer_gl_buffer(g_buffer: GBuffer) -> GlBuffer:
    return g_buffer._gl_buffer


class _WriteGBuffer(NamedTuple):
    data: Buffer
    offset: int


class EditGBuffer:
    def __init__(self, g_buffer: GBuffer):
        self._g_buffer = g_buffer
        self._write_buffer: list[_WriteGBuffer] = []

    def write(self, data: Buffer, *, offset: int = 0) -> None:
        self._write_buffer.append(_WriteGBuffer(data, offset))

    def flush(self) -> None:
        if not self._write_buffer:
            return

        GBufferTarget.ARRAY.g_buffer = self._g_buffer

        self._write_buffer.sort(key=lambda w: w.offset)
        data = bytearray(self._write_buffer[0].data)
        offset = self._write_buffer[0].offset
        for write in islice(self._write_buffer, 1, None):
            if write.offset == offset + len(data):
                data += write.data
            else:
                write_gl_buffer_target_data(GL_ARRAY_BUFFER, data, offset)
                data = bytearray(write.data)
                offset = write.offset
        write_gl_buffer_target_data(GL_ARRAY_BUFFER, data, offset)
        self._write_buffer.clear()

    def clear(self) -> None:
        self._write_buffer.clear()

    @property
    def g_buffer(self) -> GBuffer:
        return self._g_buffer


class _ShaderStorageBufferBind:
    _refs: int = 0

    def __init__(self, g_buffer: GBuffer):
        self._g_buffer = g_buffer

    def __enter__(self) -> int:
        if self._refs == 0:
            self._g_buffer._bind_shader_storage_buffer_unit()
        self._refs += 1
        assert self._g_buffer._shader_storage_buffer_unit is not None
        return self._g_buffer._shader_storage_buffer_unit

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self._refs -= 1
        if self._refs == 0:
            self._g_buffer._unbind_shader_storage_buffer_unit()
        assert self._refs >= 0


def bind_g_buffer_shader_storage_buffer_unit(g_buffer: GBuffer) -> _ShaderStorageBufferBind:
    return _ShaderStorageBufferBind(g_buffer)
