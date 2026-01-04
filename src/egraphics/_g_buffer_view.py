from __future__ import annotations

__all__ = ["GBufferView", "bind_g_buffer_view_shader_storage_buffer_unit"]

import ctypes
from ctypes import sizeof as c_sizeof
from struct import unpack as c_unpack
from typing import Any
from typing import ClassVar
from typing import Final
from typing import Generator
from typing import Generic
from typing import TypeVar
from typing import overload

import emath

from ._egraphics import GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS_VALUE
from ._egraphics import set_shader_storage_buffer_unit
from ._g_buffer import GBuffer
from ._g_buffer import get_g_buffer_gl_buffer
from ._state import register_reset_state_callback
from ._weak_fifo_set import WeakFifoSet

_BVT = TypeVar(
    "_BVT",
    ctypes.c_float,
    ctypes.c_double,
    ctypes.c_int8,
    ctypes.c_uint8,
    ctypes.c_int16,
    ctypes.c_uint16,
    ctypes.c_int32,
    ctypes.c_uint32,
    emath.FVector2,
    emath.DVector2,
    emath.IVector2,
    emath.I8Vector2,
    emath.I16Vector2,
    emath.I32Vector2,
    emath.UVector2,
    emath.U8Vector2,
    emath.U16Vector2,
    emath.U32Vector2,
    emath.FVector3,
    emath.DVector3,
    emath.IVector3,
    emath.I8Vector3,
    emath.I16Vector3,
    emath.I32Vector3,
    emath.UVector3,
    emath.U8Vector3,
    emath.U16Vector3,
    emath.U32Vector3,
    emath.FVector4,
    emath.DVector4,
    emath.IVector4,
    emath.I8Vector4,
    emath.I16Vector4,
    emath.I32Vector4,
    emath.UVector4,
    emath.U8Vector4,
    emath.U16Vector4,
    emath.U32Vector4,
    emath.FMatrix2x2,
    emath.DMatrix2x2,
    emath.FMatrix2x3,
    emath.DMatrix2x3,
    emath.FMatrix2x4,
    emath.DMatrix2x4,
    emath.FMatrix3x2,
    emath.DMatrix3x2,
    emath.FMatrix3x3,
    emath.DMatrix3x3,
    emath.FMatrix3x4,
    emath.DMatrix3x4,
    emath.FMatrix4x2,
    emath.DMatrix4x2,
    emath.FMatrix4x3,
    emath.DMatrix4x3,
    emath.FMatrix4x4,
    emath.DMatrix4x4,
)

_CTYPES_TO_STRUCT_NAME: Final[dict[Any, str]] = {
    ctypes.c_float: "=f",
    ctypes.c_double: "=d",
    ctypes.c_int8: "=b",
    ctypes.c_uint8: "=B",
    ctypes.c_int16: "=h",
    ctypes.c_uint16: "=H",
    ctypes.c_int32: "=i",
    ctypes.c_uint32: "=I",
}


_ARRAY_TO_BUFFER_VIEW_TYPE: Final = {
    emath.FVector2Array: emath.FVector2,
    emath.DVector2Array: emath.DVector2,
    emath.I8Vector2Array: emath.I8Vector2,
    emath.U8Vector2Array: emath.U8Vector2,
    emath.I16Vector2Array: emath.I16Vector2,
    emath.U16Vector2Array: emath.U16Vector2,
    emath.I32Vector2Array: emath.I32Vector2,
    emath.U32Vector2Array: emath.U32Vector2,
    emath.FVector3Array: emath.FVector3,
    emath.DVector3Array: emath.DVector3,
    emath.I8Vector3Array: emath.I8Vector3,
    emath.U8Vector3Array: emath.U8Vector3,
    emath.I16Vector3Array: emath.I16Vector3,
    emath.U16Vector3Array: emath.U16Vector3,
    emath.I32Vector3Array: emath.I32Vector3,
    emath.U32Vector3Array: emath.U32Vector3,
    emath.FVector4Array: emath.FVector4,
    emath.DVector4Array: emath.DVector4,
    emath.I8Vector4Array: emath.I8Vector4,
    emath.U8Vector4Array: emath.U8Vector4,
    emath.I16Vector4Array: emath.I16Vector4,
    emath.U16Vector4Array: emath.U16Vector4,
    emath.I32Vector4Array: emath.I32Vector4,
    emath.U32Vector4Array: emath.U32Vector4,
    emath.FMatrix2x2Array: emath.FMatrix2x2,
    emath.DMatrix2x2Array: emath.DMatrix2x2,
    emath.FMatrix2x3Array: emath.FMatrix2x3,
    emath.DMatrix2x3Array: emath.DMatrix2x3,
    emath.FMatrix2x4Array: emath.FMatrix2x4,
    emath.DMatrix2x4Array: emath.DMatrix2x4,
    emath.FMatrix3x2Array: emath.FMatrix3x2,
    emath.DMatrix3x2Array: emath.DMatrix3x2,
    emath.FMatrix3x3Array: emath.FMatrix3x3,
    emath.DMatrix3x3Array: emath.DMatrix3x3,
    emath.FMatrix3x4Array: emath.FMatrix3x4,
    emath.DMatrix3x4Array: emath.DMatrix3x4,
    emath.FMatrix4x2Array: emath.FMatrix4x2,
    emath.DMatrix4x2Array: emath.DMatrix4x2,
    emath.FMatrix4x3Array: emath.FMatrix4x3,
    emath.DMatrix4x3Array: emath.DMatrix4x3,
    emath.FMatrix4x4Array: emath.FMatrix4x4,
    emath.DMatrix4x4Array: emath.DMatrix4x4,
    emath.FArray: ctypes.c_float,
    emath.DArray: ctypes.c_double,
    emath.I8Array: ctypes.c_int8,
    emath.U8Array: ctypes.c_uint8,
    emath.I16Array: ctypes.c_int16,
    emath.U16Array: ctypes.c_uint16,
    emath.I32Array: ctypes.c_int32,
    emath.U32Array: ctypes.c_uint32,
}


def _get_size_of_bvt(t: type[_BVT]) -> int:
    try:
        return t.get_size()  # type: ignore
    except AttributeError:
        return c_sizeof(t)  # type: ignore


@register_reset_state_callback
def _reset_g_buffer_view_shader_storage_buffer_state() -> None:
    GBufferView._max_shader_storage_buffer_unit = None
    GBufferView._next_shader_storage_buffer_unit = 0
    GBufferView._unbound_shader_storage_buffer_units.clear()


class GBufferView(Generic[_BVT]):
    _max_shader_storage_buffer_unit: ClassVar[int | None] = None
    _next_shader_storage_buffer_unit: ClassVar[int] = 0
    _unbound_shader_storage_buffer_units: ClassVar[WeakFifoSet[GBufferView]] = WeakFifoSet()
    _open_shader_storage_buffer_units: ClassVar[set[int]] = set()

    def __init__(
        self,
        g_buffer: GBuffer,
        data_type: type[_BVT],
        *,
        length: int | None = None,
        stride: int | None = None,
        offset: int = 0,
        instancing_divisor: int | None = None,
    ) -> None:
        self._g_buffer = g_buffer
        self._data_type: type[_BVT] = data_type

        if stride is None:
            stride = _get_size_of_bvt(data_type)
        if stride < 1:
            raise ValueError("stride must be greater than 0")
        self._stride = stride

        if offset < 0:
            raise ValueError("offset must be 0 or greater")
        self._offset = offset

        if length is None:
            length = len(g_buffer) - self._offset
        if length < 0:
            raise ValueError("length must be 0 or greater")
        self._length = length

        if self._offset + length > len(g_buffer):
            raise ValueError("length/offset goes beyond buffer size")

        if instancing_divisor is not None:
            if instancing_divisor < 1:
                raise ValueError("instancing divisor must be greater than 0")
        self._instancing_divisor = instancing_divisor
        self._shader_storage_buffer_unit: int | None = None

    def __len__(self) -> int:
        stride_diff = self._stride - _get_size_of_bvt(self._data_type)
        return (self._length + stride_diff) // self._stride

    def __iter__(self) -> Generator[_BVT, None, None]:
        if len(self._g_buffer) == 0:
            return
        buffer = memoryview(self._g_buffer)
        for i in range(len(self)):
            start_index = self._offset + (self._stride * i)
            end_index = start_index + _get_size_of_bvt(self._data_type)
            chunk = buffer[start_index:end_index]
            try:
                struct_name = _CTYPES_TO_STRUCT_NAME[self._data_type]
                data = c_unpack(struct_name, chunk)[0]
            except KeyError:
                data = self._data_type.from_buffer(chunk)
            yield data  # type: ignore

    @property
    def g_buffer(self) -> GBuffer:
        return self._g_buffer

    @property
    def data_type(self) -> type[_BVT]:
        return self._data_type

    @property
    def data_type_size(self) -> int:
        return _get_size_of_bvt(self._data_type)

    @property
    def length(self) -> int:
        return self._length

    @property
    def stride(self) -> int:
        return self._stride

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def instancing_divisor(self) -> int | None:
        return self._instancing_divisor

    def _acquire_shader_storage_buffer_unit(self) -> None:
        if self._open_shader_storage_buffer_units:
            self._shader_storage_buffer_unit = self._open_shader_storage_buffer_units.pop()
            return
        assert self._next_shader_storage_buffer_unit <= GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS_VALUE
        if self._next_shader_storage_buffer_unit == GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS_VALUE:
            self._steal_shader_storage_buffer_unit()
        else:
            self._shader_storage_buffer_unit = self._next_shader_storage_buffer_unit
            GBufferView._next_shader_storage_buffer_unit += 1

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
            g_buffer_view = self._unbound_shader_storage_buffer_units.pop()
        except IndexError:
            raise RuntimeError("no shader storage buffer unit available")
        g_buffer_view._release_shader_storage_buffer_unit()
        self._acquire_shader_storage_buffer_unit()

    def _bind_shader_storage_buffer_unit(self) -> int:
        if self._stride != self.data_type_size:
            raise RuntimeError(
                f"stride must match data_type_size for shader storage buffer binding"
            )
        if self._instancing_divisor is not None:
            raise RuntimeError("instancing_divisor must be None for shader storage buffer binding")
        if self._shader_storage_buffer_unit is None:
            self._acquire_shader_storage_buffer_unit()
        assert self._shader_storage_buffer_unit is not None
        gl_buffer = get_g_buffer_gl_buffer(self._g_buffer)
        set_shader_storage_buffer_unit(
            self._shader_storage_buffer_unit, gl_buffer, self._offset, self._length
        )
        return self._shader_storage_buffer_unit

    def _unbind_shader_storage_buffer_unit(self) -> None:
        assert self._shader_storage_buffer_unit is not None
        self._unbound_shader_storage_buffer_units.add(self)

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FVector2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FVector2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.DVector2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.DVector2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I8Vector2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I8Vector2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U8Vector2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U8Vector2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I16Vector2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I16Vector2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U16Vector2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U16Vector2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I32Vector2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I32Vector2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U32Vector2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U32Vector2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FVector3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FVector3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.DVector3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.DVector3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I8Vector3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I8Vector3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U8Vector3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U8Vector3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I16Vector3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I16Vector3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U16Vector3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U16Vector3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I32Vector3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I32Vector3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U32Vector3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U32Vector3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FVector4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FVector4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.DVector4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.DVector4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I8Vector4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I8Vector4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U8Vector4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U8Vector4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I16Vector4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I16Vector4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U16Vector4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U16Vector4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I32Vector4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.I32Vector4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U32Vector4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.U32Vector4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix2x2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix2x2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix2x3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix2x3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix2x4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix2x4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix3x2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix3x2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix3x3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix3x3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix3x4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix3x4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix4x2Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix4x2]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix4x3Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix4x3]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FMatrix4x4Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[emath.FMatrix4x4]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.FArray, *, instancing_divisor: int | None = None
    ) -> GBufferView[ctypes.c_float]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.DArray, *, instancing_divisor: int | None = None
    ) -> GBufferView[ctypes.c_double]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I8Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[ctypes.c_int8]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U8Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[ctypes.c_uint8]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I16Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[ctypes.c_int16]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U16Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[ctypes.c_uint16]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.I32Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[ctypes.c_int32]: ...

    @overload
    @classmethod
    def from_array(
        cls, array: emath.U32Array, *, instancing_divisor: int | None = None
    ) -> GBufferView[ctypes.c_uint32]: ...

    @classmethod
    def from_array(
        cls,
        array: emath.FVector2Array
        | emath.DVector2Array
        | emath.I8Vector2Array
        | emath.U8Vector2Array
        | emath.I16Vector2Array
        | emath.U16Vector2Array
        | emath.I32Vector2Array
        | emath.U32Vector2Array
        | emath.FVector3Array
        | emath.DVector3Array
        | emath.I8Vector3Array
        | emath.U8Vector3Array
        | emath.I16Vector3Array
        | emath.U16Vector3Array
        | emath.I32Vector3Array
        | emath.U32Vector3Array
        | emath.FVector4Array
        | emath.DVector4Array
        | emath.I8Vector4Array
        | emath.U8Vector4Array
        | emath.I16Vector4Array
        | emath.U16Vector4Array
        | emath.I32Vector4Array
        | emath.U32Vector4Array
        | emath.FMatrix2x2Array
        | emath.DMatrix2x2Array
        | emath.FMatrix2x3Array
        | emath.DMatrix2x3Array
        | emath.FMatrix2x4Array
        | emath.DMatrix2x4Array
        | emath.FMatrix3x2Array
        | emath.DMatrix3x2Array
        | emath.FMatrix3x3Array
        | emath.DMatrix3x3Array
        | emath.FMatrix3x4Array
        | emath.DMatrix3x4Array
        | emath.FMatrix4x2Array
        | emath.DMatrix4x2Array
        | emath.FMatrix4x3Array
        | emath.DMatrix4x3Array
        | emath.FMatrix4x4Array
        | emath.DMatrix4x4Array
        | emath.FArray
        | emath.DArray
        | emath.I8Array
        | emath.U8Array
        | emath.I16Array
        | emath.U16Array
        | emath.I32Array
        | emath.U32Array,
        *,
        instancing_divisor: int | None = None,
    ) -> GBufferView:
        data_type = _ARRAY_TO_BUFFER_VIEW_TYPE[type(array)]
        buffer = GBuffer(array)
        return GBufferView(buffer, data_type, instancing_divisor=instancing_divisor)


class _ShaderStorageBufferBind:
    _refs: int = 0

    def __init__(self, g_buffer_view: GBufferView):
        self._g_buffer_view = g_buffer_view
        self._unit: int | None = None

    def __enter__(self) -> int:
        if self._refs == 0:
            self._unit = self._g_buffer_view._bind_shader_storage_buffer_unit()
        self._refs += 1
        assert self._unit is not None
        return self._unit

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self._refs -= 1
        if self._refs == 0:
            assert self._unit is not None
            self._g_buffer_view._unbind_shader_storage_buffer_unit()
        assert self._refs >= 0


def bind_g_buffer_view_shader_storage_buffer_unit(
    g_buffer_view: GBufferView,
) -> _ShaderStorageBufferBind:
    return _ShaderStorageBufferBind(g_buffer_view)
